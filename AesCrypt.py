import sys
sys.path.append('LocalLab')
from Crypto.Cipher import AES

class AesCrypt:
    def __init__(self,publicMths):
        self.ErrorCode = 0
        self.SendKey = b'AAAAAAAAAAAAAAAA'
        self.RecvKey = b'BBBBBBBBBBBBBBBB'
        self.Model = AES.MODE_CBC
        self.IV = bytes([0x12, 0x34, 0x56, 0x78, 0x90, 0xAB, 0xCD, 0xEF, 0x12, 0x34, 0x56, 0x78, 0x90, 0xAB, 0xCD, 0xEF])
        self.PublicMethod = publicMths

    def EnCrypt(self,data):
        byteRetData = b''
        try:
            aes = AES.new(self.SendKey,self.Model,self.IV)
            byteRetData = aes.encrypt(data)
        except BaseException as e:
            byteRetData = b''
            self.ErrorCode = 1
        return byteRetData

    def DeCrypt(self,data):
        byteRetData = b''

        try:
            aes = AES.new(self.RecvKey,self.Model,self.IV)
            byteRetData = aes.decrypt(data)
        except BaseException as e:
            byteRetData = b''
            self.ErrorCode = 2
        return byteRetData

    def GetErrorCode(self):
        return self.ErrorCode

    def GetAesBlockingSize(self):
        return AES.block_size