import socket


def start_server(host: str = "127.0.0.1", port: int = 5000) -> None:
    """
    Запускает TCP-сервер, который принимает одно соединение
    и отвечает клиенту сообщением "Привет, клиент!".
    """
    # Создаем сокет (IPv4, TCP)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))  # привязываем к адресу
        server_socket.listen(1)  # слушаем (1 соединение в очереди)

        print(f"Сервер запущен на {host}:{port}, ожидаем подключение...")

        conn, addr = server_socket.accept()  # принимаем клиента
        with conn:
            print(f"Клиент подключился: {addr}")
            conn.sendall("Привет, клиент!".encode("utf-8"))


if __name__ == "__main__":
    start_server()

