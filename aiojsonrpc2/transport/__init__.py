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

    async def close(self):
        await self.writer.close()


class Iterator:
    def __init__(self, transport):
        self.queue = asyncio.Queue()
        self.transport = transport
        self.length = 0

    def __aiter__(self):
        return self

    def __len__(self):
        return self.length

    async def __anext__(self):
        if self.queue.qsize() == 0:
            try:
                stanzas = await self.transport.receive_json()
            except RuntimeError: # transport is closed
                raise StopAsyncIteration
            if not isinstance(stanzas, list):
                stanzas = [stanzas]
            self.length = len(stanzas)
            for stanza in stanzas:
                assert isinstance(stanza, dict), "stanza must be dict, not %s" % type(stanza)
                assert stanza['jsonrpc'] == "2.0", "Only jsonrpc 2.0 is handled"
                await self.queue.put(stanza)
        try:
            return await self.queue.get()
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise e
            # else the loop is closed, Queue yell for nothing
