#!/usr/bin/env python3
"""
Одноразовый TCP-сервер:
- слушает localhost:5000
- принимает одно подключение
- отправляет клиенту "Hello, client!"
- завершает работу
"""

from __future__ import annotations
import socket
import struct
import logging
import sys
from contextlib import closing

HOST = "127.0.0.1"   # локальная машина; для внешнего доступа поменяйте на 0.0.0.0
PORT = 5000
ACCEPT_TIMEOUT_S = 15.0
IO_TIMEOUT_S = 5.0

# Настраиваем логирование (понятные, короткие сообщения)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

def send_msg(sock: socket.socket, payload: bytes) -> None:
    """Фрейминг: 4 байта длины в network byte order (big-endian) + тело."""
    header = struct.pack("!I", len(payload))
    sock.sendall(header + payload)

def serve_once() -> int:
    # создаём слушающий сокет
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as srv:
        # безопасный перезапуск без "Address already in use"
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # привязка и начало прослушивания
        srv.bind((HOST, PORT))
        srv.listen(1)  # нам нужен ровно один клиент
        srv.settimeout(ACCEPT_TIMEOUT_S)

        logging.info("Server is listening on %s:%d …", HOST, PORT)

        try:
            conn, addr = srv.accept()  # ждём одного клиента
        except socket.timeout:
            logging.error("No client connected within %ss — exiting.", ACCEPT_TIMEOUT_S)
            return 1

        with closing(conn):
            logging.info("Client connected from %s:%d", *addr)
            conn.settimeout(IO_TIMEOUT_S)

            # готовим и отправляем полезную нагрузку
            message = "Hello, client!".encode("utf-8")
            try:
                send_msg(conn, message)
                logging.info("Message sent (%d bytes).", len(message))
            except (BrokenPipeError, ConnectionResetError) as e:
                logging.error("Send failed: %s", e)
                return 1

            # корректное полузакрытие записи (по желанию)
            try:
                conn.shutdown(socket.SHUT_WR)
            except OSError:
                # уже закрыт или платформа не поддерживает — не критично
                pass

        logging.info("Done. Bye.")
        return 0

if __name__ == "__main__":
    try:
        sys.exit(serve_once())
    except KeyboardInterrupt:
        logging.warning("Interrupted by user.")
        sys.exit(130)
