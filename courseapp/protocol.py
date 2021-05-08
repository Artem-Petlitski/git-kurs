"""Custom protocol on top of TCP/IP"""
from json import dumps


def send(socket, data):
    if type(data) == dict:
        data = dumps(data)
    else:
        data = str(data)
    data = bytes(data, encoding="utf8")
    size = len(b"1234567890" + data)
    data = bytes(str(size).zfill(10), encoding="utf8") + data
    sent_overall = 0
    while sent_overall < size:
        sent = socket.send(data[sent_overall:])
        if sent == 0:
            raise RuntimeError("Подключение разорвано")
        sent_overall += sent


def receive(socket):
    chunks = socket.recv(1024)
    size = int(chunks[:10])
    bytes_received = len(chunks)
    chunks = chunks[10:]
    while bytes_received < size:
        chunk = socket.recv(min(size - bytes_received, 1024))
        if chunk == "":
            raise RuntimeError("Подключение разорвано")
        chunks += chunk
        bytes_received += len(chunk)
    return chunks.decode("utf8")


GOOD = "GOOD"
ERROR = "ERROR"
BREAK = "BREAK"
