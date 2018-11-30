import logging
from aiohttp import web

from aiojsonrpc2.server import Session
from aiojsonrpc2.client import Client

logging.basicConfig(level=logging.DEBUG)


async def jsonrpc_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    session = Session(ws, request)
    @session.handler('hello')
    async def hello(name, __context=None):
        print("ctx", __context)
        return "Hello {}".format(name)

    await session.run()
    return ws


async def test_jsonrpc(aiohttp_client, loop):
    app = web.Application()
    app.router.add_get('/', jsonrpc_handler)

    client = await aiohttp_client(app)
    ws = await client.ws_connect('/')

    c = Client(ws)
    proxy = c.proxy()
    print(proxy)
    r = await proxy.hello('world')
    logging.debug('response %s', r)
    assert r == "Hello world"
    c.close()
