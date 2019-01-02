import logging
import asyncio

from aiohttp import web
from prometheus_async import aio

from aiojsonrpc2.client import Client
from aiojsonrpc2.transport.http import handler_factory, HTTPClient
from tests.utils import hello, let_it_crash


async def test_http(aiohttp_client, loop):
    app = web.Application()
    app.router.add_post('/', handler_factory(hello))
    app.router.add_get("/metrics", aio.web.server_stats)
    client = await aiohttp_client(app)
    async with Client(HTTPClient(client, '/')) as c:
        r = await c.stub.hello('world')
        logging.debug('response %s', r)
        assert r == "Hello world"
        resp = await client.get("/metrics")
        assert resp.status == 200
        text = await resp.text()
        print(text)


async def test_http_batch(aiohttp_client, loop):
    app = web.Application()
    app.router.add_post('/', handler_factory(hello=hello))
    client = await aiohttp_client(app)
    c = Client(HTTPClient(client, '/'))
    with c.batch() as b:
        r1 = b.hello("Alice")
        r2 = b.hello("Bob")
    await asyncio.gather(r1, r2)
    assert await r1 == "Hello Alice"
    assert await r2 == "Hello Bob"
    await c.close()


async def test_http_exception(aiohttp_client, loop):
    app = web.Application()
    app.router.add_post('/', handler_factory(hello=hello,
                                             let_it_crash=let_it_crash))
    client = await aiohttp_client(app)
    async with Client(HTTPClient(client, '/')) as c:
        r = await c.stub.hello('world')
        logging.debug('response %s', r)
        assert r == "Hello world"
        try:
            r = await c.stub.let_it_crash()
        except Exception as e:
            pass # it's OK
        else:
            assert False
