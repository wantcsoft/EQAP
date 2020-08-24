import  socket
import time

g_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
g_addr = ('192.168.100.224',1000)
g_client.connect(g_addr)
nIndex = 0

while nIndex < 100:
    g_client.send("Client send data test {}\r".format(nIndex).encode())
    time.sleep(0.1)
    nIndex += 1