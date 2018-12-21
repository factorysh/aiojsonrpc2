import uuid
from typing import Any
from asyncio import Future, Queue
from collections import defaultdict


class Run:
    def __init__(self):
        self.messages = []
        self.queue = Queue()

    def append(self, message: Any=None) -> int:
        self.messages.append(message)
        self.queue.put_nowait(None)
        return len(self.messages)

    async def wait(self):
        while self.queue.qsize() > 0:
            await self.queue.get()


class Longrun:
    def __init__(self, loop=None, maxsize=0):
        self.loop = loop
        self.maxsize = maxsize
        self.runs = defaultdict(Run) # FIXME clean it later

    async def next(self, rid: str="", latest: int=0) -> list:
        assert rid != "", "rid can't be null"
        r = self.runs[rid]
        f = await r.wait()
        if len(r.messages) > latest:
            return [[i + latest, v] for i, v in
                    enumerate(r.messages[latest:])]
        return None

    def add(self, rid: str="", message: Any= None) -> int:
        assert rid != "", "rid can't be null"
        r = self.runs[rid]
        return r.append(message)

