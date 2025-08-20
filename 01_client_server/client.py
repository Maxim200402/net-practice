import socket


def start_client(host: str = "127.0.0.1", port: int = 5000) -> None:
    """
    Подключается к серверу и получает сообщение.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))  # подключаемся к серверу
        data = client_socket.recv(1024)  # получаем до 1024 байт
        print("Сообщение от сервера:", data.decode("utf-8"))


if __name__ == "__main__":
    start_client()

