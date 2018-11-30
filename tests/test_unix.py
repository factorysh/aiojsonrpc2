import asyncio

from aiojsonrpc2.transport import PascalStringTransport
from aiojsonrpc2.server import Session


async def on_client(reader: asyncio.StreamReader,
                    writer: asyncio.StreamWriter):
    transport = PascalStringTransport(reader, writer)
    session = Session(transport)
    await session.run()


async def build_server(path="/tmp/jsonrpc"):
    server = asyncio.start_unix_server(on_client, path=path)
    @server.handler
    async def hello(name, __context=None):
        return "Hello %s" % name
