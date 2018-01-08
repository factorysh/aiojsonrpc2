import logging
from aiohttp import web

from aiojsonrpc2 import Session

logging.basicConfig(level=logging.DEBUG)


async def plop(request, ws, req):
    logging.debug(req.params)
    ws.send_json(dict(jsonrpc="2.0", id=req._id,
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
    await j.send_json(dict(jsonrpc="2.0", method="plop", id=0,
                           params=dict(hello='world')))
    r = await j.receive_json()
    logging.debug(r)
    print(r)
