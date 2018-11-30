import asyncio
import aiohttp

from aiojsonrpc2.client import Client


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:8080') as ws:
            c = Client(ws)
            proxy = c.proxy()
            r = await proxy.hello('world')
            print(r)
            c.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
