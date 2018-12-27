import asyncio
from random import random


async def hello(name, __context=None):
    await asyncio.sleep(random())
    return "Hello %s" % name

