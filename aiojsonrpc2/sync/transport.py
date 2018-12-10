import struct
import json
import socket
import io


class SyncPascalStringTransport:

    def __init__(self, sock: socket.socket):
        self.sock = sock

    def send_json(self, msg):
        blob = json.dumps(msg).encode('utf8')
        self.send_raw(blob)

    def send_raw(self, blob):
        if isinstance(blob, str):
            blob = blob.encode('utf8')
        self.sock.sendall(struct.pack('i', len(blob)))
        self.sock.sendall(blob)

    def receive_raw(self) -> str:
        l = struct.unpack('i', readexactly(self.sock, 4))[0]
        return readexactly(self.sock, l).decode('utf8')

    def receive_json(self):
        return json.loads(self.receive_raw())


def readexactly(sock: socket.socket, size: int) -> bytes:
    chunk = sock.recv(size)
    if len(chunk) == size:
        return chunk
    total = len(chunk)
    buff = io.BytesIO(size)
    buff.write(buff)
    while total < size:
        chunk = sock.recv(size)
        buff.write(chunk)
        total += len(chunk)
    return buff.getvalue()
