from random import random
import logging
from asyncio import Queue, sleep, ensure_future

from aiojsonrpc2.session import Session
from tests.utils import hello, let_it_crash


logging.basicConfig(level=logging.DEBUG)


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


async def test_session(loop):
    #loop.set_debug(True)
    t = TransportMockup()
    s = Session(dict(hello=hello), t)
    task = ensure_future(s.run())

    await t.r.put(dict(jsonrpc='2.0', method="hello", id=0, params=["Alice"]))
    r = await t.w.get()
    print("rr:", r)
    assert r['result'] == "Hello Alice"
    assert r['id'] == 0
    print("closing")
    await s.join()
    task.cancel()
    s.close()


async def test_session_error(loop):
    #loop.set_debug(True)
    t = TransportMockup()
    s = Session(dict(hello=hello, let_it_crash=let_it_crash), t)
    task = ensure_future(s.run())
    await t.r.put(dict(jsonrpc='2.0', method="hello", id=0, params=["Alice"]))
    await t.r.put(dict(jsonrpc='2.0', method="let_it_crash", id=1, params=[]))
    r1 = await t.w.get()
    r2 = await t.w.get()
    print("r1:", r1)
    print("r2:", r2)
    await s.join()
    task.cancel()
    s.close()


async def test_session_multiple(loop):
    #loop.set_debug(True)
    t = TransportMockup()
    s = Session(dict(hello=hello), t)
    task = ensure_future(s.run())

    await t.r.put(dict(jsonrpc='2.0', method="hello", id=0, params=["Alice"]))
    await t.r.put(dict(jsonrpc='2.0', method="hello", id=1, params=["Bob"]))
    r1 = await t.w.get()
    r2 = await t.w.get()
    print("r1:", r1)
    print("r2:", r2)
    print("closing")
    await s.join()
    task.cancel()
    s.close()


async def test_batch(loop):
    t = TransportMockup()
    s = Session(dict(hello=hello), t)
    task = ensure_future(s.run())
    await t.r.put([
        dict(jsonrpc='2.0', method="hello", id=0, params=["Alice"]),
        dict(jsonrpc='2.0', method="hello", id=1, params=["Bob"])
    ])
    for a in range(2):
        r = await t.w.get()
        print("r#", a, r)
    await s.join()
    task.cancel()
    s.close()


async def test_batch_batch(loop):
    t = TransportMockup()
    s = Session(dict(hello=hello), t, same_batch_size=True)
    task = ensure_future(s.run())
    await t.r.put([
        dict(jsonrpc='2.0', method="hello", id=0, params=["Alice"]),
        dict(jsonrpc='2.0', method="hello", id=1, params=["Bob"])
    ])
    r = await t.w.get()
    print("r", r)
    await s.join()
    task.cancel()
    s.close()
