import asyncio
import logging
import json
import functools

from jsonrpc.jsonrpc2 import JSONRPC20Request, JSONRPC20Response
from jsonrpc.exceptions import (
    JSONRPCInvalidParams,
    JSONRPCInvalidRequest,
    JSONRPCInvalidRequestException,
    JSONRPCMethodNotFound,
    JSONRPCParseError,
    JSONRPCServerError,
    JSONRPCDispatchException,
)
from aiojsonrpc2.transport import AbstractTransport


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


async def async_response(r, writer, _id):
    await writer.send_json(dict(jsonrpc="2.0", id=_id, result=await r))


class Session:

    def __init__(self, methods: dict, transport: AbstractTransport, context: Context=None):
        self.ids = set()
        self.transport = transport
        if context is None:
            context = Context()
        self.context = context
        self.queue_req = asyncio.Queue()
        self.queue_resp = asyncio.Queue()
        self.methods = methods
        self.reading_task = asyncio.Future()
        self.reading = True
        self.tasks = dict()

    async def run(self):
        self.task_requests = asyncio.ensure_future(self.requests())
        self.task_responses = asyncio.ensure_future(self.responses())
        while self.reading:
            try:
                req = await self.queue_req.get()
            except RuntimeError:
                return
            if req.method not in self.methods:
                logging.error("Unknown method: %s" % req.method)
                await write_error(self.transport, req._id,
                                    JSONRPCMethodNotFound())
                return
            f = self.methods[req.method]
            try:
                if isinstance(req.params, list):
                    t = asyncio.ensure_future(f(*req.params,
                                                __context=self.context))
                else: # It's a dict
                    req.params['__context'] = self.context
                    t = asyncio.ensure_future(f(**req.params))

                asyncio.ensure_future(self._response(req._id, t))
                self.tasks[req._id] = t
                #def clean_task(f):
                    #del self.tasks[req._id]
                #t.add_done_callback(clean_task)
            except Exception as e:
                await write_error(self.transport, req._id,
                                    JSONRPCServerError(message=str(e)))
                return

    async def _response(self, _id, future):
        r = await future
        await self.queue_resp.put(dict(jsonrpc="2.0", id=_id, result=r))

    async def join(self):
        asyncio.gather(self.queue_req.join(), self.queue_resp.join())
        asyncio.gather(*self.tasks.values())

    def close(self):
        self.transport.close()
        self.reading = False
        self.reading_task.set_result(None)
        self.task_requests.cancel()
        self.task_responses.cancel()

    async def requests(self):
        while self.reading:
            try:
                reqs = await self.transport.receive_json()
            except RuntimeError: # transport is closed
                return
            for req in list(jsonrpcrequest(reqs)):
                assert req._id not in self.ids, "Replayed id: %s" % req._id
                self.ids.add(req._id)
                await self.queue_req.put(req)

    async def responses(self):
        while self.reading:
            try:
                r = await self.queue_resp.get()
            except RuntimeError:
                return
            await self.transport.send_json(r)

