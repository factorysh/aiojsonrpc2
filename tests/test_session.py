from random import random
from asyncio import Queue, sleep, ensure_future

from aiojsonrpc2.session import Session


async def hello(name, __context=None):
    await sleep(random())
    return "Hello %s" % name


class TransportMockup:
    def __init__(self):
        self.r = Queue()
        self.w = Queue()

    async def receive_json(self):
        return await self.r.get()

    async def send_json(self, msg):
        await self.w.put(msg)

    def close(self):
        pass


async def test_sesison(loop):
    t = TransportMockup()
    s = Session(t)
    s.register(hello=hello)
    assert s['hello'] == hello
    assert 'hello' in s
    assert await s['hello']("World") == "Hello World"

    await t.r.put(dict(jsonrpc='2.0', method="hello", id=0, params=["Alice"]))
    s.read_all_the_things()
    async for req in s:
        print("req:", req.params)
        return
    s.close()


