import socket
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

HOST, PORT = "127.0.0.1", 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(3)
    logging.info("Server listening on %s:%d", HOST, PORT)

    for i in range(3):  # примем три клиента подряд
        conn, addr = srv.accept()
        logging.info("Accepted connection %d from %s", i+1, addr)
        conn.sendall(f"Hello, client {i+1}!".encode("utf-8"))
        conn.close()

    logging.info("Server done, bye.")

