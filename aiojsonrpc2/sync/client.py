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
        return _response(self.client.tr.receive_json())


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
    def stub(self):
        return Stub(self)

    def batch(self):
        return Batch(self)


class Stub:
    def __init__(self, client: SyncUnixClient):
        self.client = client

    def __getattr__(self, method) -> Method:
        return Method(self.client, method)


class LaterMethod:
    def __init__(self, batch, method):
        self.batch = batch
        self.method = method

    def __call__(self, *args, **kwargs):
        assert len(args) == 0 or len(kwargs) == 0, \
            "You can use positional or named args, not both"
        if len(args) == 0:
            params = kwargs
        else:
            params = list(args)
        _id = self.batch._client.id()
        req = JSONRPC20Request(_id=_id,
                               method=self.method,
                               params=params)
        self.batch._batch.append(req)
        return _id


def _response(raw):
    raw['_id'] = raw['id']
    return JSONRPC20Response(**raw)


class Batch:
    _client = None
    _batch = []

    def __init__(self, client: SyncUnixClient):
        self._client = client

    def __getattr__(self, method: str) -> LaterMethod:
        return LaterMethod(self, method)

    def __call__(self):
        batch = JSONRPC20BatchRequest(*self._batch)
        self._client.tr.send_raw(batch.json)
        resp = self._client.tr.receive_json()
        if isinstance(resp, list):
            return JSONRPC20BatchResponse(*[_response(r) for r in resp])
        return _response(resp)
