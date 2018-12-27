import asyncio


class AbstractTransport:
    def __init__(self, reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer

    async def send_json(self, msg): # jsonrpc2 stanza
        pass

    async def receive_json(self): # returns jsonrpc2 stanza
        pass

    def close(self):
        self.writer.close()
