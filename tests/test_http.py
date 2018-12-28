import logging
import asyncio

from aiohttp import web

from aiojsonrpc2.client import Client
from aiojsonrpc2.transport.http import handler_factory, JSONRequest
from tests.utils import hello


async def test_http(aiohttp_client, loop):
    app = web.Application()
    app.router.add_post('/', handler_factory(hello=hello))
    client = await aiohttp_client(app)
    c = Client(JSONRequest(client, '/'))
    r = await c.stub.hello('world')
    logging.debug('response %s', r)
    assert r == "Hello world"


async def test_http_batch(aiohttp_client, loop):
    app = web.Application()
    app.router.add_post('/', handler_factory(hello=hello))
    client = await aiohttp_client(app)
    c = Client(JSONRequest(client, '/'))
    with c.batch() as b:
        r1 = b.hello("Alice")
        r2 = b.hello("Bob")
    await asyncio.gather(r1, r2)
    assert r1.result() == "Hello Alice"
    assert r2.result() == "Hello Bob"
