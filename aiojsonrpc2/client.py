import logging
import asyncio

from aiojsonrpc2.transport import AbstractTransport, Iterator
from aiojsonrpc2 import exceptions


class Method:
    def __init__(self, client, method):
        self.client = client
        self.method = method

    async def __call__(self, *args, **kwargs):
        assert len(args) == 0 or len(kwargs) == 0, \
            "You can use positional or named args, not both"
        _id = self.client.id()
        if len(args) == 0:
            params = kwargs
        else:
            params = list(args)
        req = dict(jsonrpc="2.0", id=_id, method=self.method, params=params)
        self.client.queries[_id] = asyncio.Future()
        await self.client.transport.send_json(req)
        resp = await self.client.queries[_id]
        return resp


class Client:
    def __init__(self, transport: AbstractTransport):
        self.transport = transport
        self._id = 0
        self.queries = dict()
        self.responses = Iterator(transport)
        self.task_run = asyncio.ensure_future(self.run())

    async def run(self):
        async for resp in self.responses:
            _id = resp['id']
            assert _id in self.queries, "Unknown response id : %s" % _id
            if 'error' in resp:
                e = exceptions.from_data(resp)
                # FIXME e doesn't inherate from Exception
                self.queries[_id].set_exception(Exception(e))
            else:
                self.queries[_id].set_result(resp['result'])

    async def __aenter__(self):
        return self

    async def __aexit__(self, type, value, traceback):
        await self.close()

    async def close(self):
        await self.transport.close()
        self.task_run.cancel()

    def id(self):
        self._id += 1
        return self._id

    @property
    def stub(self):
        return Stub(self)

    def batch(self):
        return Batch(self)


class Stub:
    def __init__(self, client: Client):
        self.client = client

    def __getattr__(self, method) -> Method:
        return Method(self.client, method)


class LaterMethod:
    def __init__(self, batch, method):
        self.batch = batch
        self.method = method

    def __call__(self, *args, **kwargs):
        assert len(args) == 0 or len(kwargs) == 0, \
            "You can use positional or named args, not both"
        if len(args) == 0:
            params = kwargs
        else:
            params = list(args)
        _id = self.batch._client.id()
        self.batch._batch.append(dict(
            jsonrpc="2.0",
            id=_id,
            params=params,
            method=self.method
        ))
        f = asyncio.Future()
        self.batch._client.queries[_id] = f
        self.batch._responses.append(f)
        return f


class Batch:
    _client = None
    _batch = []
    _responses = []

    def __init__(self, client: Client):
        self._client = client

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return asyncio.ensure_future(self())

    def __getattr__(self, method: str) -> LaterMethod:
        return LaterMethod(self, method)

    async def __call__(self):
        await self._client.transport.send_json(self._batch)
        asyncio.gather(*self._responses)

