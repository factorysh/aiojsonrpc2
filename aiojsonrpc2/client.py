import logging
import asyncio

from aiojsonrpc2.transport import AbstractTransport, Iterator


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
            assert _id in self.queries, "Unknown response id"
            self.queries[_id].set_result(resp['result'])

    def close(self):
        self.transport.close()
        self.task_run.cancel()

    def id(self):
        self._id += 1
        return self._id

    @property
    def stub(self):
        return Stub(self)


class Stub:
    def __init__(self, client: Client):
        self.client = client

    def __getattr__(self, method) -> Method:
        return Method(self.client, method)

