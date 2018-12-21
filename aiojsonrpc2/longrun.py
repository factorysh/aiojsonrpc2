import uuid
from typing import Any
from asyncio import Future, Queue
import uuid


class Run:
    def __init__(self):
        self.messages = []
        self.queue = Queue()

    def append(self, message: Any=None) -> int:
        self.messages.append(message)
        self.queue.put_nowait(None)
        return len(self.messages)

    async def purge(self):
        while self.queue.qsize() > 0:
            await self.queue.get()

    async def get(self, latest: int=0) -> list:
        await self.queue.get()
        await self.purge()
        if len(self.messages) > latest:
            return [[i+latest, v] for i, v in enumerate(self.messages[latest:])]
        return []


class Longrun:
    def __init__(self, loop=None, maxsize=0):
        self.loop = loop
        self.maxsize = maxsize
        self.runs = dict() # FIXME clean it later

    # expose this method
    async def next(self, rid: str="", latest: int=0) -> list:
        assert rid != "", "rid can't be null"
        return await self.runs[rid].get(latest)

    def new(self) -> str:
        rid = str(uuid.uuid4())
        self.runs[rid] = Run()
        return rid

    def add(self, rid: str="", message: Any= None) -> int:
        assert rid != "", "rid can't be null"
        return self.runs[rid].append(message)

    def close(self, rid: str=""):
        assert rid != "", "rid can't be null"
        del self.runs[rid]
