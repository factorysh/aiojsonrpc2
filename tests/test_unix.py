import asyncio
from pathlib import Path

from aiojsonrpc2.transport import PascalStringTransport
from aiojsonrpc2.server import Session
from aiojsonrpc2.client import Client


async def on_client(reader: asyncio.StreamReader,
                    writer: asyncio.StreamWriter):
    transport = PascalStringTransport(reader, writer)
    session = Session(transport)
    @session.handler("hello")
    async def hello(name, __context=None):
        return "Hello %s" % name

    await session.run()


async def build_server(path="/tmp/jsonrpc", loop=None):
    return await asyncio.start_unix_server(on_client, path=path, loop=loop)


async def test_jsonrpc(loop):
    path = Path("/tmp/jsonrpc")
    if path.is_file():
        path.unlink()
    server = await asyncio.start_unix_server(on_client, path=path, loop=loop)

    async with server:
        assert path.is_socket(), "Path not found"
        transport = PascalStringTransport(*( await asyncio.\
                                            open_unix_connection(path,
                                                                 loop=loop)))
        client = Client(transport)
        p = client.proxy()
        r = await p.hello("World")
        print(r)
        client.close()
        server.close()
