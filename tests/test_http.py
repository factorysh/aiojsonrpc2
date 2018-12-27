import logging
import asyncio

from aiohttp import web

from aiojsonrpc2.client import Client
from aiojsonrpc2.transport.http import handler_factory, JSONRequest
from tests.utils import hello


async def test_jsonrpc(aiohttp_client, loop):
    app = web.Application()
    app.router.add_post('/', handler_factory(hello=hello))
    client = await aiohttp_client(app)
    c = Client(JSONRequest(client, '/'))
    r = await c.stub.hello('world')
    logging.debug('response %s', r)
    assert r == "Hello world"
