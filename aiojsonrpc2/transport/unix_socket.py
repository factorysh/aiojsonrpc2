import asyncio

from aiojsonrpc2.session import Session
from aiojsonrpc2.client import Client
from aiojsonrpc2.transport.pascal_string import PascalStringTransport


def on_unix_client(handlers):
    async def on_client(reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
        transport = PascalStringTransport(reader, writer)
        session = Session(handlers, transport)
        await session.run()
    return on_client


async def UnixServer(path, loop=None, **handlers):
    return await asyncio.start_unix_server(on_unix_client(handlers),
                                             path=str(path),
                                             loop=loop)


async def UnixClient(path, loop=None) -> Client:
    r, w=await asyncio.open_unix_connection(str(path), loop=loop)
    return Client(PascalStringTransport(r, w))
