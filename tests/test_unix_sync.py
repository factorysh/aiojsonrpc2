import os
import socket
import time
from multiprocessing import Process
from pathlib import Path

from jsonrpc import JSONRPCResponseManager, dispatcher
from jsonrpc.jsonrpc2 import JSONRPC20Request

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
        print("command", command.data)
        response = JSONRPCResponseManager.handle_request(command, dispatcher)
        print('server response', response.data)
        tr.send_json(response.data)
        connection.close()


def test_unix_sync():
    path = "/tmp/sync_server.socket"
    p = Process(target=server, args=(path, ) )
    p.start()
    time.sleep(1)
    client = SyncUnixClient(path)
    resp = client.proxy.hello("World")
    print('client response', resp.data)
    assert resp._id == 0
    assert resp.result == "Hello World"
    p.kill()
