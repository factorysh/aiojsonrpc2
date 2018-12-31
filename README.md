AIO Jsonrpc2
============

Asyncio [jsonrpc2](http://www.jsonrpc.org/specification) implementation.

Asyncio before python 3.5 is just boring, so this library needs Python 3.5 or 3.6

This library handles unix socket, websocket, and plain old HTTP transports.

Test it
-------

    make test


Curl demo
---------

A simple server :

```python
#!/usr/bin/env python3
from aiohttp import web

from aiojsonrpc2.transport.http import handler_factory


async def hello(name: str):
    return "Hello %s" % name


app = web.Application()
app.add_routes([web.post('/', handler_factory(hello))])

web.run_app(app)
```

Simple curl query

    $ curl -v \
        -XPOST \
        -H "Content-Type: application/json" \
        --data '{"jsonrpc":"2.0", "method":"hello", "params":["World"]}' \
        http://localhost:8080/

Async client
------------

### Stub

```python
from aiojsonrpc2.client import UnixClient

path = '/tmp/jsonrpc.socket'

# you are somewhere in an await function, with a loop
client = await UnixClient(path)
resp = await client.stub.hello("World")
assert resp == "Hello World"
```

### Batch

Batch is handled by asyncio

```python
import asyncio
from aiojsonrpc2.client import UnixClient

path = '/tmp/jsonrpc.socket'
# you are somewhere in an await function, with a loop
client = await UnixClient(path)

r_a = asyncio.ensure_future(client.stub.hello("Alice"))
r_b = asyncio.ensure_future(client.stub.hello("Bob"))

await asyncio.gather(r_a, r_b)

assert r_a.result() == "Hello Alice"
assert r_b.result() == "Hello Bob"
```

Sync client
-----------

For nia nia nia compatibility, with flask or wathever, a sync client is provided.

### Stub

Stub object wraps the distant API.

```python
from aiojsonrpc2.sync.client import SyncUnixClient


path = '/tmp/jsonrpc.socket'
client = SyncUnixClient(path)
resp = client.stub.hello("World") # hello method, with ["World"] arguments
```

### Batch

You can ask multiple question in a batch.

Batch object can be used like the Stub object.

```python
from aiojsonrpc2.sync.client import SyncUnixClient

path = '/tmp/jsonrpc.socket'
client = SyncUnixClient(path)
batch = client.batch()
id_a = batch.hello("Alice")
id_b = batch.hello("Bob")
resp = batch()
resp_a, resp_b = resp.responses # responses are sorted
```

Licence
-------

3 terms BSD licence, © 2018 Mathieu Lecarme
