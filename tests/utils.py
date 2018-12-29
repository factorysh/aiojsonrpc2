import asyncio
from random import random


async def hello(name, __context=None):
    await asyncio.sleep(random())
    return "Hello %s" % name


async def let_it_crash(__context=None):
    await asyncio.sleep(random())
    1/0

