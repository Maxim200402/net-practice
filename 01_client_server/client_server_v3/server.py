"""
Одноразовый TCP-сервер:
- слушает localhost:5000
- принимает одно подключение
- читает length-prefixed запрос от клиента
- отправляет клиенту "Hello, client!"
- завершает работу
"""

from __future__ import annotations
import socket
import struct
import logging
import sys
import json

HOST = "127.0.0.1"
PORT = 5000
ACCEPT_TIMEOUT_S = 15.0
IO_TIMEOUT_S = 5.0
MAX_MSG_SIZE = 10_000_000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

def recvn(sock: socket.socket, n: int) -> bytes:
    chunks, remaining = [], n
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

def serve_once() -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((HOST, PORT))
            srv.listen(1)
            srv.settimeout(ACCEPT_TIMEOUT_S)

            logging.info("Сервер слушает %s:%d …", HOST, PORT)

            try:
                conn, addr = srv.accept()
            except socket.timeout:
                logging.error("Клиент не подключился за %s сек — выходим.", ACCEPT_TIMEOUT_S)
                return 1

            with conn:
                logging.info("Клиент подключился с %s:%d", *addr)
                conn.settimeout(IO_TIMEOUT_S)

                try:
                    req = recv_msg(conn)
                    try:
                        j = json.loads(req.decode("utf-8"))
                        logging.info("Запрос (JSON): %s", j)
                    except Exception:
                        logging.info("Запрос (raw %d байт): %r", len(req), req[:200])
                except Exception:
                    logging.error("Ошибка при чтении запроса.", exc_info=True)
                    return 1

                message = "Hello, client!".encode("utf-8")
                try:
                    send_msg(conn, message)
                    logging.info("Сообщение отправлено (%d байт).", len(message))
                except (BrokenPipeError, ConnectionResetError, TimeoutError, OSError):
                    logging.error("Ошибка при отправке клиенту.", exc_info=True)
                    return 1

                try:
                    conn.shutdown(socket.SHUT_WR)
                except OSError:
                    pass

        logging.info("Работа завершена. Пока.")
        return 0

    except OSError:
        logging.error("Ошибка при инициализации сервера (bind/listen). Порт занят?", exc_info=True)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(serve_once())
    except KeyboardInterrupt:
        logging.warning("Остановлено пользователем.")
        sys.exit(130)

