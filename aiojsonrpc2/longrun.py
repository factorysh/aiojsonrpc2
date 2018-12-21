import uuid
from typing import Any
from asyncio import Queue, get_running_loop
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
    def __init__(self, loop=None, maxsize=0, maxage=300):
        if loop is None:
            self.loop = get_running_loop()
        else:
            self.loop = loop
        self.maxsize = maxsize
        self.maxage = maxage
        self.runs = dict()

    # expose this method
    async def next(self, rid: str="", latest: int=0) -> list:
        assert rid != "", "rid can't be null"
        return await self.runs[rid].get(latest)

    async def new(self) -> str:
        rid = str(uuid.uuid4())
        self.runs[rid] = Run()
        self.loop.call_later(self.maxage, self.lazy_close, rid)
        return rid

    def add(self, rid: str, message: Any) -> int:
        assert rid != "", "rid can't be null"
        return self.runs[rid].append(message)

    def lazy_close(self, rid):
        if rid in self.runs:
            self.close(rid)

    def close(self, rid: str):
        assert rid != "", "rid can't be null"
        del self.runs[rid]
