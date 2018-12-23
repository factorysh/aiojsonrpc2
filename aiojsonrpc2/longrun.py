"""
Handling slow RPC, with an event flow, or in fire and forget

 * Call a RPC, get an id.
 * Call for next batch events, with theirs positions.
 * Call for more batch events, starting at latest known events

"""
from typing import Any
from asyncio import get_running_loop
import uuid
from enum import Enum

from aiojsonrpc2.waiter import Waiter


States = Enum('States', 'queued running canceled error success')


class Run:
    def __init__(self):
        self.messages = []
        self.waiter = Waiter()

    def append(self, message: Any = None) -> int:
        self.messages.append(message)
        self.waiter.done()
        return len(self.messages)

    async def get(self, latest: int = 0) -> list:
        await self.waiter.wait()
        if len(self.messages) > latest:
            return [dict(id=i+latest, value=v, state=States.running.name) for
                         i, v in enumerate(self.messages[latest:])]
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
    async def next(self, rid: str = "", latest: int = 0) -> list:
        assert rid != "", "rid can't be null"
        return await self.runs[rid].get(latest)

    def new(self) -> str:
        rid = str(uuid.uuid4())
        self.runs[rid] = Run()
        self.runs[rid].timeout = self.loop.call_later(self.maxage, self.lazy_close, rid)
        return rid

    def add(self, rid: str, message: Any) -> int:
        assert rid != "", "rid can't be null"
        return self.runs[rid].append(message)

    def lazy_close(self, rid):
        if rid in self.runs:
            self.close(rid)

    def close(self, rid: str):
        assert rid != "", "rid can't be null"
        self.runs[rid].timeout.cancel()
        del self.runs[rid]
