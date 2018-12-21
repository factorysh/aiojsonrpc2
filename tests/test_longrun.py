from aiojsonrpc2.longrun import Longrun
from asyncio import ensure_future


async def test_longrun(loop):
    l = Longrun(loop)

    f1 = ensure_future(l.next("plop"))

    n = l.add("plop", 42)
    assert len(l.runs["plop"].messages) == 1
    assert n == 1
    l.add("plop", "aussi")
    assert len(l.runs["plop"].messages) == 2
    v1 = await f1
    print(v1)
    v2 = await l.next("plop")
    print(v2)

