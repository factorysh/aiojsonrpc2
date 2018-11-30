from aiohttp import web
import logging

from aiojsonrpc2.server import Session


async def hello(name, __context=None):
    logging.debug(__context)
    return "Hello {}".format(name)


async def jsonrpc_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    session = Session(ws, request)
    session['hello'] = hello

    await session.run()
    return ws

app = web.Application()
app.router.add_get('/', jsonrpc_handler)
web.run_app(app)

