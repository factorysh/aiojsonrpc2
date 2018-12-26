import struct
import asyncio
import json


class PascalStringTransport:

    def __init__(self, reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer

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