import json
from asyncio import Queue

from aiohttp.web import StreamResponse, json_response
from aiojsonrpc2.session import Session


class JSONRequest:
    def __init__(self, client, uri="/"):
        self.client = client
        self.uri = uri
        self.queue = Queue()

    async def send_json(self, data):
        r = await self.client.post(self.uri, json=data)
        await self.queue.put(await r.json())

    async def receive_json(self):
        return await self.queue.get()


class HttpRW:
    def __init__(self, request):
        self.request = request
        self.queue = Queue()

    async def receive_json(self):
        assert self.request.body_exists, "Body must exist"
        return await self.request.json()

    async def send_json(self, data):
        await self.queue.put(data)

    async def json(self):
        return await json_response(await self.queue.get())


def handler_factory(**methods):
    async def jsonrpc_handler(request):
        t = HttpRW(request)
        session = Session(t, request)
        for name, function in methods.items():
            session[name] = function
        await session.run()
        return t.json()
    return jsonrpc_handler
