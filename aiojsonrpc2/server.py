import logging
import asyncio
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
from aiojsonrpc2.transport import PascalStringTransport


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
        self.queue = list()
        self.methods = dict()

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

    async def __anext__(self) -> JSONRPC20Request:
        while len(self.queue) == 0:
            msg = None
            try:
                msg = await self.ws.receive_json()
            except TypeError as e:
                logging.debug(e)
                continue
            except RuntimeError as e:
                if e.args[0] == 'WebSocket connection is closed.':
                    raise StopAsyncIteration
                raise e
            finally:
                if msg is not None:
                    logging.debug(msg)
                    self.queue = list(jsonrpcrequest(msg))
        req = self.queue.pop()
        _id = req._id
        if _id in self.ids:
            raise Exception("Replayed id")
        self.ids.add(_id)
        return req


def on_unix_client(**handlers):
    async def on_client(reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
        transport = PascalStringTransport(reader, writer)
        session = Session(transport)
        for method, func in handlers.items():
            session[method] = func
        await session.run()
    return on_client


async def UnixServer(path, loop=None, **handlers):
    server = await asyncio.start_unix_server(on_unix_client(**handlers),
                                             path=str(path),
                                             loop=loop)
    print("server started:", path)
    return server
