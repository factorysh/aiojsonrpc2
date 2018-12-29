import asyncio
import json
import logging

from aiohttp import web, WSMsgType

from aiojsonrpc2.session import Session
from aiojsonrpc2.transport import AbstractTransport


class WebsocketTransport(AbstractTransport):
    def __init__(self, ws):
        self.ws = ws

    async def receive_json(self):
        while True:
            msg = await self.ws.receive()
            logging.debug('msg: %s %s' % (msg.type, msg))
            if msg.type == WSMsgType.TEXT:
                return json.loads(msg.data)
            elif msg.type == WSMsgType.CLOSE:
                raise StopAsyncIteration
            elif msg.type == WSMsgType.ERROR:
                logging.error('ws connection closed with exception %s' %
                      self.ws.exception())
                raise StopAsyncIteration

    async def send_json(self, msg):
        return await self.ws.send_json(msg)

    async def close(self):
        await self.ws.close()


def handler_factory(**methods):
    """
    Return a aiohttp.Handler exposing methods
    """
    async def jsonrpc_handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        assert not ws.closed
        t = WebsocketTransport(ws)
        session = Session(methods, t, request)
        await session.run()
        return ws

    return jsonrpc_handler
