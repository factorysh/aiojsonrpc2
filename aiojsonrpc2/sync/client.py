from pathlib import Path
import socket

from aiojsonrpc2.sync.transport import SyncPascalStringTransport

from jsonrpc.jsonrpc2 import JSONRPC20Request, JSONRPC20Response


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

        self.client._id += 1
        req = JSONRPC20Request(_id=self.client._id,
                               method=self.method, params=params)
        self.client.responses[self.client._id] = None
        self.client.tr.send_json(req.data)
        resp = self.client.tr.receive_json()
        resp['_id'] = resp['id']
        resp = JSONRPC20Response(**resp)
        return resp


class SyncUnixClient:
    def __init__(self, path):
        assert Path(path).exists()
        self._id = -1
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(path)
        self.tr = SyncPascalStringTransport(client)
        self.responses = dict()

    @property
    def proxy(self):
        return Proxy(self)


class Proxy:
    def __init__(self, client: SyncUnixClient):
        self.client = client

    def __getattr__(self, method) -> Method:
        return Method(self.client, method)
