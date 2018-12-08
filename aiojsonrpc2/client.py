import logging
import asyncio

from aiohttp import web


class Method:
    def __init__(self, client, method):
        self.client = client
        self.method = method

    async def __call__(self, *args, **kwargs):
        assert len(args) == 0 or len(kwargs) == 0, \
            "You can use positional or named args, not both"
        _id = self.client.id()
        if len(args) == 0:
            params = kwargs
        else:
            params = list(args)
        req = dict(jsonrpc="2.0", id=_id, method=self.method, params=params)
        self.client.responses[_id] = asyncio.Future()
        await self.client.ws.send_json(req)
        resp = await self.client.responses[_id]
        return resp


class Client:
    def __init__(self, ws: web.WebSocketResponse):
        self.ws = ws
        self._id = 0
        self.responses = dict()
        self.listen = True
        self.listen_task = asyncio.ensure_future(self.listen_responses())
        self.handlers = dict()

    async def listen_responses(self):
        while self.listen:
            try:
                resp = await self.ws.receive_json()
            except TypeError as e:
                continue
            except RuntimeError as e:
                if e.args[0] == 'WebSocket connection is closed.':
                    return
                else:
                    raise e
            else:
                logging.debug(resp)
                assert resp['jsonrpc'] == "2.0"
                if 'id' in resp:
                    self.responses[resp['id']].set_result(resp['result'])
                else: # it's an event
                    m = resp['method']
                    if m in self.handlers:
                        params = resp['params']
                        if isinstance(params, list):
                            await self.handlers[m](*params)
                        else: # it's a dict
                            await self.handlers[m](**params)
                    else:
                        logging.info("Unknown event: %s" % m)

    def close(self):
        self.listen = False
        self.listen_task.cancel()

    def handler(self, name: str):
        assert isinstance(name, str)
        def decorator(func):
            assert asyncio.iscoroutinefunction(func)
            self.handlers[name] = func
            return func
        return decorator

    def id(self):
        self._id += 1
        return self._id

    def proxy(self):
        return Proxy(self)


class Proxy:
    def __init__(self, client: Client):
        self.client = client

    def __getattr__(self, method) -> Method:
        return Method(self.client, method)

