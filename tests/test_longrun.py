from aiojsonrpc2.longrun import Longrun
from asyncio import ensure_future


async def test_longrun(loop):
    l = Longrun(loop)

    chan = l.new()
    f1 = ensure_future(l.next(chan))

    n = l.add(chan, 42)
    assert len(l.runs[chan].messages) == 1
    assert n == 1
    l.add(chan, "aussi")
    assert len(l.runs[chan].messages) == 2
    v1 = await f1
    print("v1", v1)
    assert len(v1) == 2

