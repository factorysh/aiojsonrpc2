#!/usr/bin/env python3

from aiohttp import web

from tests.utils import hello
from aiojsonrpc2.transport.http import handler_factory

app = web.Application()
app.add_routes([web.post('/', handler_factory(hello))])

web.run_app(app)
