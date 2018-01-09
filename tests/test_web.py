import logging
from aiohttp import web

from aiojsonrpc2.server import Session
from aiojsonrpc2.client import Client

logging.basicConfig(level=logging.DEBUG)


async def plop(request, ws, req):
    logging.debug(req.params)
    await ws.send_json(dict(jsonrpc="2.0", id=req._id,
                            result="Hello {}".format(req.params['hello'])))


async def jsonrpc_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    session = Session(ws, request)
    session['plop'] = plop

    await session.run()
    return ws


async def test_jsonrpc(test_client, loop):
    app = web.Application()
    app.router.add_get('/', jsonrpc_handler)
    logging.debug(app)

    client = await test_client(app)

    j = await client.ws_connect('/')
    c = Client(j)
    proxy = c.proxy()
    r = await proxy.plop(hello='world')
    logging.debug('response %s', r)
    print(r)
    assert r == "Hello world"
    c.close()
