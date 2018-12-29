import asyncio
import json

from aiohttp import web, WSMsgType

from aiojsonrpc2.session import Session
from aiojsonrpc2.transport import AbstractTransport


class WebsocketTransport(AbstractTransport):
    def __init__(self, ws):
        self.ws = ws

    async def receive_json(self):
        while True:
            print("server ws.closed:", self.ws.closed)
            msg = await self.ws.receive()
            print('msg:', msg.type, msg)
            if msg.type == WSMsgType.TEXT:
                return json.loads(msg.data)

    async def send_json(self, msg):
        return await self.ws.send_json(msg)

    async def close(self):
        await self.ws.close()


def handler_factory(**methods):
    """
    Return a aiohttp.Handler exposing methods
    """
    async def jsonrpc_handler(request):
        print("server request:", request)
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        assert not ws.closed
        print("server ws:", ws)
        t = WebsocketTransport(ws)
        session = Session(methods, t, request)
        await session.run()
        #session_task = asyncio.ensure_future(session.run())
        return ws

    return jsonrpc_handler
