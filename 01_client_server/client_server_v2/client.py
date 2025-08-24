from __future__ import annotations
import socket
import struct
import logging

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

def start_client(host: str = HOST, port: int = PORT, timeout_s: float = IO_TIMEOUT_S) -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout_s)
            s.connect((host, port))
            logging.info("Подключились к %s:%d", host, port)

            # 1) читаем 4 байта длины
            header = recvn(s, 4)
            (length,) = struct.unpack("!I", header)

            if length > MAX_MSG_SIZE:
                raise ValueError(f"Слишком большое сообщение: {length} байт (> {MAX_MSG_SIZE})")

            # 2) читаем ровно length байт полезной нагрузки
            payload = recvn(s, length)

            text = payload.decode("utf-8")
            print("Сообщение от сервера:", text)

    except (EOFError, TimeoutError, ConnectionError, OSError, ValueError):
        logging.error("Ошибка на стороне клиента.", exc_info=True)

if __name__ == "__main__":
    start_client()
