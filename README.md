AIO Jsonrpc2
============

Asyncio [jsonrpc2](http://www.jsonrpc.org/specification) implementation.

Asyncio before python 3.5 is just boring, so this library needs Python 3.5 or 3.6

Test it
-------

    make test


Async client
------------

```python
from aiojsonrpc2.client import UnixClient

path = '/tmp/jsonrpc.socket'

# you are somewhere in an await function, with a loop
client = await UnixClient(path)
resp = await client.stub.hello("World")
```

Sync client
-----------

For nia nia nia compatibility, with flask or wathever, a sync client is provided.

### Proxy

Proxy object wrap the distant API.

```python
from aiojsonrpc2.sync.client import SyncUnixClient


path = '/tmp/jsonrpc.socket'
client = SyncUnixClient(path)
resp = client.stub.hello("World") # hello method, with ["World"] arguments
```

### Batch

You can ask multiple question in a batch.
The responses can be unsorted, but each response has its own id.

Batch object can be used like the Proxy object.

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
