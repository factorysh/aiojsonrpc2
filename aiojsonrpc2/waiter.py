from typing import Any
from collections import defaultdict
from asyncio import Future


class Waiter:
    def __init__(self, size=1):
        self.size = size
        self.cpt = 0
        self.future = Future()

    def reset(self):
        self.future = Future()
        self.cpt = 0

    def incr(self):
        self.size += 1

    async def wait(self):
        v = await self.future
        self.reset()
        return v

    def done(self):
        self.cpt += 1
        if self.cpt == self.size:
            self.future.set_result(None)


class MultiWaiter(Waiter):
    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.wait()

