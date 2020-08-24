import socket
import select

class SocketClient:
    def __init__(self,strHostIP, nHostPortNum,fTimeOut,pubMethod):
        self.Addr = (strHostIP,int(nHostPortNum))
        self.TimeOut = fTimeOut
        self.PublicMethod = pubMethod
    
    def SendDataToServer(self,data):
        recvData = b''

        try:
            self.socketClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except socket.error as e:
            print("Create socket client with error:{}".format(e))
            return recvData

        try:
            print(self.Addr)
            self.socketClient.connect(self.Addr)
        except socket.gaierror as e:
            print("Server address related with error:{}".format(e))
            return recvData
        except socket.error as e:
            print("Connect to server with error:{}".format(e))
            return recvData


        try:
            nDataLen = len(data)
            while nDataLen > 0:
                nLenSend = self.socketClient.send(data)
                dataLeft = data[nLenSend:nDataLen]
                nDataLen = len(dataLeft)
        except socket.error as e:
            print("Send data to server with error:{}".format(e))
            return recvData

        try:
            recvData = self.socketClient.recv(1024)
            print("Receive data len:",len(recvData))
        except socket.error as e:
            print("Receive data from server with error:".format(e))
        return recvData



        # try:
        #     self.socketClient = socket(AF_INET,SOCK_STREAM)
        #     self.socketClient.settimeout(self.TimeOut)
        #     self.socketClient.setblocking(False)
        #     print('Socket blocking flag:',self.socketClient.getblocking())
        #     nConnCode = self.socketClient.connect_ex(self.Addr)
        #
        #     if(nConnCode != 0):
        #         print("Connect to server with error:{}".format(nConnCode))
        #         self.PublicMethod.Log('Connect to server with error and the ErrorCode:{}'.format(nConnCode))
        #         return recvData
        #
        #     nSendDatalen = self.socketClient.send(data)
        #     self.PublicMethod.Log("Send data to server ok, data len:".format(nSendDatalen))
        #     recvData = self.socketClient.recv(4096)
        # except BaseException as e:
        #     self.PublicMethod.Log('Communication with server with :{}'.format(e))
        # finally:
        #     self.socketClient.close()
        # return recvData

