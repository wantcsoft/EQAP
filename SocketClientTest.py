import socket
import time

# g_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# g_addr = ('192.168.100.224',1000)
# g_client.connect(g_addr)
# nIndex = 0
#
# while nIndex < 100:
#     g_client.send("Client send data test {}\r".format(nIndex).encode())
#     time.sleep(0.1)
#     nIndex += 1


socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "122.144.182.35"
port = 6433
try:
    socketClient.connect((host, port))
except socket.gaierror as e:
    print("Server address related with error:{}".format(e))

except socket.error as e:
    print("Connect to server with error:{}".format(e))

print(socketClient.send(b"hello world"))
print(socketClient.recv(1024))
