import logging
import asyncio

from aiohttp import web

from aiojsonrpc2.session import Session
from aiojsonrpc2.client import Client
from aiojsonrpc2.transport.websocket import handler_factory

logging.basicConfig(level=logging.DEBUG)


async def hello(name, __context=None):
    print("ctx", __context)
    asyncio.sleep(2)
    return "Hello {}".format(name)


async def test_jsonrpc(aiohttp_client, loop):
    app = web.Application()
    app.router.add_get('/', handler_factory(hello=hello))

    client = await aiohttp_client(app)
    ws = await client.ws_connect('/')

    c = Client(ws)
    r = await c.stub.hello('world')
    logging.debug('response %s', r)
    assert r == "Hello world"
    c.close()
