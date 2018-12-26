import asyncio
import logging
import json

from jsonrpc.jsonrpc2 import JSONRPC20Request
from jsonrpc.exceptions import (
    JSONRPCInvalidParams,
    JSONRPCInvalidRequest,
    JSONRPCInvalidRequestException,
    JSONRPCMethodNotFound,
    JSONRPCParseError,
    JSONRPCServerError,
    JSONRPCDispatchException,
)
from aiohttp.web import WebSocketResponse, Request


def jsonrpcrequest(data):
    if isinstance(data, list):
        for d in data:
            yield JSONRPC20Request.from_data(d)
    else:
        yield JSONRPC20Request.from_data(data)


async def write_error(ws, _id, error):
    e = error._data
    e['id'] = _id
    await ws.send_str(json.dumps(e))
    await ws.close()


class Context:
    def __init__(self, headers=None):
        if headers is None:
            headers = dict()
        self.headers = headers


class Session:

    def __init__(self, ws: WebSocketResponse, context: Context=None):
        self.ids = set()
        self.ws = ws
        if context is None:
            context = Context()
        self.context = context
        self.queue = asyncio.Queue()
        self.methods = dict()
        self.reading_task = None
        self.reading = True

    def close(self):
        self.reading = False
        self.ws.close()
        if self.reading_task is not None:
            self.reading_task.cancel()

    def register(self, **methods):
        for name, method in methods.items():
            self[name] = method

    def __setitem__(self, name, function):
        assert asyncio.iscoroutinefunction(function)
        self.methods[name] = function

    def __getitem__(self, name):
        return self.methods[name]

    def __delitem___(self, name):
        del self.methods[name]

    def __contains__(self, name):
        return name in self.methods

    def handler(self, name: str):
        assert isinstance(name, str)
        def decorator(func):
            self[name] = func
            return func
        return decorator

    async def run(self):
        try:
            async for req in self:
                if req.method not in self:
                    logging.error("Unknown method: %s" % req.method)
                    await write_error(self.ws, req._id,
                                      JSONRPCMethodNotFound())
                    return
                f = self[req.method]
                try:
                    if isinstance(req.params, list):
                        r = await f(*req.params, __context=self.context)
                    else: # It's a dict
                        req.params['__context'] = self.context
                        r = await f(**req.params)
                    await self.ws.send_json(dict(jsonrpc="2.0", id=req._id,
                                                 result=r))
                except Exception as e:
                    await write_error(self.ws, req._id,
                                      JSONRPCServerError(message=str(e)))
                    return
        except json.decoder.JSONDecodeError:
            await write_error(self.ws, req._id, JSONRPCParseError())
            return

    def __aiter__(self):
        return self

    async def requests(self):
        while self.reading:
            try:
                reqs = await self.ws.receive_json()
            except RuntimeError: # transport is closed
                return
            for req in list(jsonrpcrequest(reqs)):
                assert req._id not in self.ids, "Replayed id: %s" % req._id
                self.ids.add(req._id)
                await self.queue.put(req)

    def read_all_the_things(self):
        self.reading_task = asyncio.ensure_future(self.requests())

    async def __anext__(self) -> JSONRPC20Request:
        return await self.queue.get()
