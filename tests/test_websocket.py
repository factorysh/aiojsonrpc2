import logging
import asyncio

from aiohttp import web

from aiojsonrpc2.session import Session
from aiojsonrpc2.client import Client
from aiojsonrpc2.transport.websocket import handler_factory
from tests.utils import hello

logging.basicConfig(level=logging.DEBUG)


async def _test_websocket(aiohttp_client, loop):
    app = web.Application()
    app.router.add_get('/', handler_factory(hello=hello))

    client = await aiohttp_client(app)
    async with client.ws_connect('/') as ws:
        c = Client(ws)
        r = await c.stub.hello('world')
        logging.debug('response %s', r)
        assert r == "Hello world"
        await c.close()


async def test_websocket_multiple(aiohttp_client, loop):
    app = web.Application()
    app.router.add_get('/', handler_factory(hello=hello))

    client = await aiohttp_client(app)
    async with client.ws_connect('/') as ws:
        c = Client(ws)
        r1 = asyncio.ensure_future(c.stub.hello('Alice'))
        r1.add_done_callback(print)
        r2 = asyncio.ensure_future(c.stub.hello('Bob'))
        r2.add_done_callback(print)
        await asyncio.gather(r1, r2)
        assert await r1 == "Hello Alice"
        assert await r2 == "Hello Bob"
        await c.close()
