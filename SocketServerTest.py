import socket


g_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
g_addr = ('192.168.8.116', 9898)
g_socket.bind(g_addr)
g_socket.listen(100)

while True:
    client, _ = g_socket.accept()
    while True:
        data = client.recv(1024)
        if not data:
            break
        print(data)
        print('Server receive data from clinet {}:'.format(client), data)
