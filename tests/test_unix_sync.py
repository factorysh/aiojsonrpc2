import os
import socket
import time
from multiprocessing import Process
from pathlib import Path

from jsonrpc import JSONRPCResponseManager, dispatcher
from jsonrpc.jsonrpc2 import JSONRPC20Request, JSONRPC20BatchResponse

from aiojsonrpc2.sync.transport import SyncPascalStringTransport
from aiojsonrpc2.sync.client import SyncUnixClient


def server(path: str):
    if os.path.exists(path):
        os.remove(path)
    print("Listening %s" % path)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(path)
    dispatcher["hello"] = lambda hello: "Hello %s" % hello
    server.listen(1)
    while True:
        connection, client_address = server.accept()
        tr = SyncPascalStringTransport(connection)
        command = JSONRPC20Request.from_data(tr.receive_json())
        print("command", command)
        response = JSONRPCResponseManager.handle_request(command, dispatcher)
        print('server response', response.data)
        tr.send_raw(response.json)
        connection.close()


def test_unix_sync():
    path = "/tmp/sync_server.socket"
    p = Process(target=server, args=(path, ) )
    p.start()
    time.sleep(1)
    client = SyncUnixClient(path)
    resp = client.stub.hello("World")
    assert resp._id == 0
    assert resp.result == "Hello World"
    p.kill()


def test_unix_batch():
    path = "/tmp/sync_server.socket"
    p = Process(target=server, args=(path, ) )
    p.start()
    time.sleep(1)
    client = SyncUnixClient(path)
    batch = client.batch()
    id_a = batch.hello("Alice")
    id_b = batch.hello("Bob")
    assert 0 == id_a
    assert 1 == id_b
    resp = batch()
    assert isinstance(resp, JSONRPC20BatchResponse)
    r_a, r_b = resp.responses
    assert r_a.result == "Hello Alice"
    assert r_b.result == "Hello Bob"
    p.kill()
