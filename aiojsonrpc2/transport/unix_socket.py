import struct
import asyncio
import json

from aiojsonrpc2.session import Session
from aiojsonrpc2.client import Client
from aiojsonrpc2.transport import AbstractTransport


class PascalStringTransport(AbstractTransport):

    async def send_json(self, msg):
        blob = json.dumps(msg).encode('utf8')
        self.writer.write(struct.pack('i', len(blob)))
        self.writer.write(blob)
        await self.writer.drain()

    async def receive_json(self):
        l = struct.unpack('i', await self.reader.readexactly(4))[0]
        blob = await self.reader.readexactly(l)
        if isinstance(blob, bytes):
            blob = blob.decode('utf8')
        return json.loads(blob)


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
