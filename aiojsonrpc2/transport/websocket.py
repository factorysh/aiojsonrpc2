import asyncio

from aiohttp import web

from aiojsonrpc2.session import Session


def handler_factory(**methods):
    """
    Return a aiohttp.Handler exposing methods
    """
    async def jsonrpc_handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        session = Session(ws, request)
        for name, function in methods.items():
            session[name] = function

        session_task = asyncio.ensure_future(session.run())

        asyncio.gather(session_task)
        return ws
    return jsonrpc_handler
