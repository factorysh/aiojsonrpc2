from typing import Any
from collections import defaultdict
from asyncio import Future


class MultiWaiter:
    def __init__(self, size=1):
        self.size = size
        self.cpt = 0
        self.f = Future()

    def __aiter__(self):
        return self

    def incr(self):
        self.size += 1

    def reset(self):
        self.cpt = 0

    async def __anext__(self):
        v = await self.f
        self.f = Future()
        self.cpt = 0
        return v

    def done(self):
        self.cpt += 1
        if self.cpt == self.size:
            self.f.set_result(None)

