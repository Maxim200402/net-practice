from __future__ import annotations
import socket
import struct
import logging
import json

HOST = "127.0.0.1"
PORT = 5000
IO_TIMEOUT_S = 5.0
MAX_MSG_SIZE = 10_000_000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

def recvn(sock: socket.socket, n: int) -> bytes:
    chunks = []
    remaining = n
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise EOFError("Соединение закрыто до получения всех данных")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)

def recv_msg(sock: socket.socket, max_size: int = MAX_MSG_SIZE) -> bytes:
    header = recvn(sock, 4)
    (length,) = struct.unpack("!I", header)
    if length > max_size:
        raise ValueError(f"Слишком большое сообщение: {length} байт (> {max_size})")
    return recvn(sock, length)

def send_msg(sock: socket.socket, payload: bytes) -> None:
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)

def start_client(host: str = HOST, port: int = PORT, timeout_s: float = IO_TIMEOUT_S) -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout_s)
            s.connect((host, port))
            logging.info("Подключились к %s:%d", host, port)

            request = json.dumps({"cmd": "ping"}).encode("utf-8")
            send_msg(s, request)
            logging.info("Отправили запрос (%d байт).", len(request))

            payload = recv_msg(s)
            text = payload.decode("utf-8")
            print("Сообщение от сервера:", text)

    except (EOFError, TimeoutError, ConnectionError, OSError, ValueError):
        logging.error("Ошибка на стороне клиента.", exc_info=True)

if __name__ == "__main__":
    start_client()

