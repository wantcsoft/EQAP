import configparser
import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler


class PublicMethods:
    def __init__(self):
        self.IsInitWithError = False
        self.ErrorCode = 0
        self.InitLoggerInfo()

    # 初始化日志记录对象
    def InitLoggerInfo(self):
        try:
            self.LogFileFormat = '/home/projects/EQAP/Log/{}.log'
            logFilePath = os.path.split(self.LogFileFormat)[0]
            if not os.path.exists(logFilePath):
                os.mkdir(logFilePath)

            self.Logger = logging.getLogger('EQAPLogger')
            self.Logger.setLevel(logging.INFO)

            logFileFullName = self.LogFileFormat.format(time.strftime("%Y-%m-%d", time.localtime()))
            lfh = TimedRotatingFileHandler(logFileFullName,when='H',backupCount=100,encoding='utf-8')
            lfh.setLevel(logging.INFO)

            formatter = logging.Formatter("%(asctime)s\t - %(filename)s[line:%(lineno)d]\t -  %(message)s")

            lfh.setFormatter(formatter)
            self.Logger.addHandler(lfh)
        except BaseException as e:
            self.IsInitWithError = True
            self.ErrorCode = self.ErrorCode & 0x02

    def GetInitWithError(self):
        return self.IsInitWithError

    def GetErrorCode(self):
        return self.ErrorCode

    # 设置是否记录日子参数
    def SetSaveLogFlag(self, nSaveLog):
        self.SaveLog = nSaveLog

    # 从配置的列表中返回键值对应的属性
    # def ReadConfig(self, strSection, strKey):
    #     return self.config.get(strSection, strKey)

    # 字节数据转换为十六进制字符串
    def BytesToHex(self, bytesData):
        return ''.join(["%02X" % x for x in bytesData]).strip()

    # 十六进制字符串转化为字节
    def HexToBytes(self, string):
        return bytes.fromhex(string)

    # 记录日志信息
    def Log(self, strMsg):
        if not self.SaveLog:
            return

        self.Logger.info(strMsg)

    # 判断是否是数字
    def IsNumeric(self, value):
        try:
            float(value)
            return True
        except ValueError:
            pass
        return False

    # 获得校验码信息
    def CalCheckCode(self, data, offset, count):
        # 向服务器发送信息前，首先对数据进行打包，计算数据包信息所需要使用的参数
        upperCrcTab = [0x0000, 0x1231, 0x2462, 0x3653, 0x48c4, 0x5af5, 0x6ca6, 0x7e97, 0x9188, 0x83b9, 0xb5ea, 0xa7db, 0xd94c, 0xcb7d, 0xfd2e, 0xef1f]
        lowerCarTab = [0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7, 0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef]

        if self.SaveLog:
            self.Logger.info("Start to calculate CheckCode and the Input is:{} {} {}".format(data,offset,count))
        code = 0
        index = offset
        try:
            while index < count + offset:
                h = (code >> 12) & 0x0f
                l = (code >> 8) & 0x0f
                tmp = ((code & 0x00ff) << 8) | data[index]
                if tmp > 65535:
                    print('Out of range')
                tmp = tmp ^ (upperCrcTab[(h - 1) + 1] ^ lowerCarTab[(l - 1) + 1])
                code = tmp
                index = index + 1

        except Exception as e:
            print('Calculate CheckCode with error')
        else:
            if self.SaveLog:
                self.Logger.info("Calculate successfully, the CODE is:{}".format(code))
        return code
