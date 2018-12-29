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
from aiojsonrpc2.transport import AbstractTransport, Iterator


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

    def __init__(self, methods: dict, transport: AbstractTransport,
                 context: Context=None, same_batch_size: bool=False):
        self.methods = methods
        self.transport = transport
        if context is None:
            context = Context()
        self.context = context
        self.same_batch_size = same_batch_size
        self.ids = set()
        self.reading_task = asyncio.Future()
        self.reading = True
        self.tasks = dict()
        self.batch_responses = []
        self.callbacks = []
        self.requests = Iterator(self.transport)

    def add_done_callback(self, cb):
        self.callbacks.append(cb)

    async def run(self):
        async for req in self.requests:
            req = JSONRPC20Request.from_data(req)
            if req._id != None:
                assert req._id not in self.ids, "Replayed id: %s" % req._id
                self.ids.add(req._id)
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
                for cb in self.callbacks:
                    t.add_done_callback(cb)
            except Exception as e:
                await write_error(self.transport, req._id,
                                    JSONRPCServerError(message=str(e)))
                return

    async def _response(self, _id, future):
        r = dict(jsonrpc="2.0", id=_id, result=await future)
        if self.same_batch_size:
            self.batch_responses.append(r)
            if len(self.batch_responses) == len(self.requests):
                await self.transport.send_json(self.batch_responses)
                self.batch_responses = []
        else:
            await self.transport.send_json(r)

    async def join(self):
        asyncio.gather(*self.tasks.values())

    def close(self):
        self.transport.close()
        self.reading = False

