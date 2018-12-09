from pathlib import Path
import socket

from aiojsonrpc2.sync.transport import SyncPascalStringTransport

from jsonrpc.jsonrpc2 import JSONRPC20Request, JSONRPC20Response, \
    JSONRPC20BatchRequest, JSONRPC20BatchResponse


class Method:
    def __init__(self, client, method):
        self.client = client
        self.method = method

    def __call__(self, *args, **kwargs):
        assert len(args) == 0 or len(kwargs) == 0, \
            "You can use positional or named args, not both"
        if len(args) == 0:
            params = kwargs
        else:
            params = list(args)

        _id = self.client.id()
        req = JSONRPC20Request(_id=_id,
                               method=self.method, params=params)
        self.client.responses[_id] = None
        self.client.tr.send_raw(req.json)
        resp = self.client.tr.receive_json()
        return JSONRPC20Response(**patch_id(resp))


class SyncUnixClient:
    def __init__(self, path):
        assert Path(path).exists()
        self._id = -1
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(path)
        self.tr = SyncPascalStringTransport(client)
        self.responses = dict()

    def id(self):
        self._id += 1
        return self._id

    @property
    def proxy(self):
        return Proxy(self)


class Proxy:
    def __init__(self, client: SyncUnixClient):
        self.client = client

    def __getattr__(self, method) -> Method:
        return Method(self.client, method)


def patch_id(r):
    r['_id'] = r['id']
    del r['id']
    return r
