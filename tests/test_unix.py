import asyncio
from pathlib import Path

from aiojsonrpc2.transport import PascalStringTransport
from aiojsonrpc2.server import Session
from aiojsonrpc2.client import UnixClient


async def on_client(reader: asyncio.StreamReader,
                    writer: asyncio.StreamWriter):
    transport = PascalStringTransport(reader, writer)
    session = Session(transport)
    @session.handler("hello")
    async def hello(name, __context=None):
        return "Hello %s" % name

    await session.run()


async def test_jsonrpc(loop):
    path = Path("/tmp/jsonrpc")
    if path.is_file():
        path.unlink()
    server = await asyncio.start_unix_server(on_client, path=str(path),
                                             loop=loop)
    assert path.exists()
    client = await UnixClient(path, loop)
    r = await client.stub.hello("World")
    print(r)
    client.close()
    server.close()
