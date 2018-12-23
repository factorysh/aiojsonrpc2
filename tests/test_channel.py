from aiojsonrpc2.pubsub import MultiWaiter
from asyncio import ensure_future


async def test_waiter(loop):
    c = MultiWaiter()
    async def starve(c, size):
        n = 0
        async for m in c:
            n += 1
            if n == size:
                return
    t = ensure_future(starve(c, 1))
    c.done()
    c.done()
    await t

