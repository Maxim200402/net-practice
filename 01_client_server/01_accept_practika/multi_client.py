import socket

HOST, PORT = "127.0.0.1", 5000

# запускаем три подключения подряд
for i in range(3):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cli:
        cli.connect((HOST, PORT))
        data = cli.recv(1024)
        print(f"Client {i+1} got:", data.decode())
