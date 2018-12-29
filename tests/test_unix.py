import asyncio
from pathlib import Path

from aiojsonrpc2.transport.unix_socket import PascalStringTransport, \
    UnixServer, UnixClient
from tests.utils import hello


async def test_jsonrpc(loop):
    path = Path("/tmp/jsonrpc")
    if path.is_file():
        path.unlink()

    server = await UnixServer(path, loop=loop, hello=hello)
    print("server", server)
    assert path.exists()
    client = await UnixClient(path, loop)
    r = await client.stub.hello("World")
    # batch

    r_a = asyncio.ensure_future(client.stub.hello("Alice"))
    r_b = asyncio.ensure_future(client.stub.hello("Bob"))

    await asyncio.gather(r_a, r_b)

    print(r_a, r_b)
    assert r_a.result() == "Hello Alice"
    assert r_b.result() == "Hello Bob"

    await client.close()
    server.close()
