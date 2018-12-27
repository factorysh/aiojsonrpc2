from random import random
import logging
from asyncio import Queue, sleep, ensure_future

from aiojsonrpc2.session import Session


logging.basicConfig(level=logging.DEBUG)


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
    loop.set_debug(True)
    t = TransportMockup()
    s = Session(dict(hello=hello), t)
    task = ensure_future(s.run())

    await t.r.put(dict(jsonrpc='2.0', method="hello", id=0, params=["Alice"]))
    r = await t.w.get()
    print("rr:", r)
    assert r.result == "Hello Alice"
    assert r._id == 0
    print("closing")
    await s.join()
    task.cancel()
    s.close()

