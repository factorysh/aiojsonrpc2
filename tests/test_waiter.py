from aiojsonrpc2.waiter import MultiWaiter, Waiter
from asyncio import ensure_future


async def test_multiwaiter(loop):
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


async def test_waiter(loop):
    w = Waiter()
    async def starve(w):
        await w.wait()
    t = ensure_future(starve(w))
    w.done()
    await t
