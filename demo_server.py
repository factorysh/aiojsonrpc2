from aiohttp import web
import logging

from aiojsonrpc2.server import Session

routes = web.RouteTableDef()


@routes.get('/')
async def jsonrpc_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    session = Session(ws, request)
    @session.handler('hello')
    async def hello(name, __context=None):
        logging.debug(__context)
        return "Hello {}".format(name)

    await session.run()
    return ws

app = web.Application()
app.add_routes(routes)
web.run_app(app)
