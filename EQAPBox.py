import time
import queue
import datetime
from SocketClient import SocketClient
from SerialPort import SerialPort
from threading import Thread
from time import sleep
from AesCrypt import AesCrypt
from PublicMethods import PublicMethods
from SqliteHelper import SqliteHelper
from Protocol.ProtocolMgmt import ProtocolMgmt


class EQAPBox:
    # 构造方法，初始化所有信息，包括读取配置
    def __init__(self):
        self.IsInitWithError = False
        # 常用的方法类，会初始化日志
        self.PublicMethod = PublicMethods()
        # 初始化失败，程序结束
        if self.PublicMethod.GetInitWithError():
            nErrCode = self.PublicMethod.GetErrorCode()
            self.PublicMethod.Log("PublicMethod class initialized with error, and the ErrorCode = {}".format(nErrCode))
            return

        self.DataStartFlag = 2
        self.DataEndFlag = 3

        self.DBFileName = './DB/Eqap.DB'
        # self.DBFileName = '/home/projects/EQAP/DB/Eqap.DB'
        self.Sqlite = SqliteHelper(self.DBFileName)
        self.SysConfig = self.Sqlite.GetSysConfig()

        self.PublicMethod.SetSaveLogFlag(self.SysConfig.SaveLog)

        self.ProtocolMgmt = ProtocolMgmt()
        lstProtocol = self.Sqlite.GetProtocolList()
        self.ProtocolMgmt.SetProtocolList(lstProtocol)

        lstProtocolMsg = self.Sqlite.GetProtocolMsgInfo()
        self.ProtocolMgmt.SetProtocolMsgList(lstProtocolMsg)

        lstProtocolMsgField = self.Sqlite.GetProtocolMsgFieldInfo()
        self.ProtocolMgmt.SetProtocolMsgFieldList(lstProtocolMsgField)

        lstChemCode = self.Sqlite.GetChemCode()
        self.ProtocolMgmt.SetChemCodeList(lstChemCode)

        lstQCSample = self.Sqlite.GetQCSampleInfo()
        self.ProtocolMgmt.SetQCSampleList(lstQCSample)

        # 定义队列，从串口获得得数据首先进入堆栈，之后才会被处理，避免可能因为处理不及时或服务器断开连接丢失数据
        self.MsgQueue = queue.Queue(maxsize=10000)

        # 加密算法类
        self.Aes = AesCrypt(self.PublicMethod)

        self.PublicMethod.Log("Start to read ini config to get deive info, TerminalID={}, TimeSequence={}, RetryTimes = {}".format(self.SysConfig.TerminalID,self.SysConfig.TimeSequence,self.SysConfig.RetryTimes))

        self.ComPorts = []
        self.DataProcessThreads = []
        self.CommDataList = []

        # 从数据库提取设备信息
        self.PublicMethod.Log("Read device info from database")
        self.Device = self.Sqlite.GetDeviceInfoFromDB()
        self.PublicMethod.Log("ip = {}, port = {}".format(self.Device.ServerIP, self.Device.ServerPort))
        # 与设备通信
        print(self.Device.ServerIP)
        print(self.Device.ServerPort)
        self.Client = SocketClient(self.Device.ServerIP, self.Device.ServerPort, self.Device.ConnToServerTimeOut, self.PublicMethod)
        # 从数据库获取仪器信息
        self.PublicMethod.Log("Read instrument info from database")
        self.LstInstr = self.Sqlite.GetInstrumentInfoFromDB()
        # 遍历仪器列表,跳过未激活设备,加入激活的设备到列表中
        for instr in self.LstInstr:
            # 跳过未激活设备
            if not instr.IsActive:
                self.PublicMethod.Log("The instrument {} is NOT active, so ignore it".format(instr.InstrumentName))
                continue
            self.PublicMethod.Log("PortName:{}, baudrate:{} for instrument:{} is open".format(instr.PortName, instr.BaudRate, instr.InstrumentName))
            serialPort = SerialPort(instr.PortName, instr.BaudRate, instr.InstrumentName, instr.ProtocolID)
            self.ComPorts.append(serialPort)
            threadSerialPort = Thread(target=EQAPBox.SerialPortReceiveDataProcess, args=(self, serialPort))
            self.DataProcessThreads.append(threadSerialPort)

        # 创建一个线程，用来处理串口读取的数据
        self.PublicMethod.Log("Create thread to process data from serial port")
        comDataProcessThread = Thread(target=EQAPBox.ProcessComData, args=(self,))
        self.DataProcessThreads.append(comDataProcessThread)
        # 创建一个线程，用来处理数据库数据
        dbDataProcessThread = Thread(target=EQAPBox.ProcessDBData, args=(self,))
        self.DataProcessThreads.append(dbDataProcessThread)
        self.StateQuery()
        # 上传数据
        self.SynchronizeChem()
        self.SynchronizeInstrInfo()
        self.Sqlite.ExecuteSqlCmd('''DELETE FROM WOR_ErrorInfo''')

    # 处理串口接收数据的方法，通过线程调用，可以同时监听多个端口
    def SerialPortReceiveDataProcess(self, comPort):
        print("Start to serial data read process, PortName:{}".format(comPort.PortName))
        while True:
            data = comPort.ReadLine()
            if not data:
                continue

            if data == '':
                continue

            if len(data) == 0:
                continue

            if data[0] != self.DataStartFlag:
                continue

            dataFromInstrument = data[1:len(data)-1]
            self.MsgQueue.put((dataFromInstrument, comPort.ProtocolID, comPort.InstrumentName))

    # 处理串口接收信息的方法
    def ProcessComData(self):
        while True:
            try:
                # nQueueSize = self.MsgQueue.qsize()
                if self.MsgQueue.empty():
                    sleep(0.002)
                    continue

                while not self.MsgQueue.empty():
                    # 从队列中提取数据
                    comData = self.MsgQueue.get()
                    data = comData[0]
                    nProtocolID = comData[1]
                    strInstrumentName = comData[2]

                    lstData = data.split(b'\x03\x02')

                    for sData in lstData:
                        # 检查信息是否定义
                        if not self.ProtocolMgmt.CheckMsgIsDefined(sData, nProtocolID):
                            continue
                        timeStr = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                        # 保存到数据库
                        bSaveData = self.Sqlite.SaveCommDataToDB((sData, 0, nProtocolID, strInstrumentName, 0, timeStr))
            except Exception:
                self.PublicMethod.Log('Process instrument communication data failed')

    # 处理数据库数据
    def ProcessDBData(self):
        while True:
            dtCurDate = datetime.datetime.now().date()
            # 清理数据库过期数据并跟新系统配置
            if self.SysConfig.LastDataCleanDate < dtCurDate:
                bCleanStatus = self.Sqlite.CleanCommDataFromDB(self.SysConfig.DataKeptDays)
                if bCleanStatus:
                    self.SysConfig.LastDataCleanDate = dtCurDate
                    self.Sqlite.UpdateSysConfig(int(self.SysConfig.SaveLog), self.SysConfig.TerminalID,
                                                self.SysConfig.TimeSequence, self.SysConfig.RetryTimes,
                                                self.SysConfig.DataKeptDays, self.SysConfig.LastDataCleanDate)

            # 方法返回的结果就是对象列表，未上传的通讯数据列表
            dataList = self.Sqlite.GetCommDataFromDB(30, self.SysConfig.RetryTimes)
            # 返回数据为空
            if len(dataList) == 0:
                sleep(3)
                continue
            # 返回数据不为空
            print('Get data from DB')
            for data in dataList:
                noResponseFromServer = False
                print(data.CommData, data.InstrumentName, data.CreateTime)
                dataSendToServer = self.ProtocolMgmt.ParseCommData(data)
                if len(dataSendToServer) == 0:
                    self.Sqlite.RemoveCommDataFromDB(data.SerialNo)
                    sleep(0.1)
                    continue

                nErrorID = 0

                for strData in dataSendToServer:
                    self.PublicMethod.Log("Data to server:" + strData)
                    byteData = bytes(strData, encoding='utf-8')
                    dataSendToServerFormatted = self.FormatComData(byteData)
                    if dataSendToServerFormatted == b'':
                        self.PublicMethod.Log("Format data failed, the original data is:".format(dataSendToServer))
                        continue
                    dataFromServer = self.Client.SendDataToServer(dataSendToServerFormatted)
                    nDataLenFromServer = len(dataFromServer)
                    if nDataLenFromServer == 0:
                        noResponseFromServer = True
                        break
                    else:
                        errorID = self.UnFormatData(dataFromServer)
                        if errorID != 0:
                            self.PublicMethod.Log("Receive error info from server")
                        else:
                            self.PublicMethod.Log("Receive data from server ok")

                        nErrorID += errorID
                    sleep(0.1)

                if noResponseFromServer:
                    print("No data from server")
                    sleep(10)
                else:
                    if nErrorID == 0:
                        data.RetryTimes = data.RetryTimes + 1
                        data.IsUploaded = 1
                        self.Sqlite.UpdateResendTimes(data.SerialNo, data.RetryTimes, data.IsUploaded)
                print('ErrorID:', nErrorID)

    # 对信息进行格式化
    def FormatComData(self, data):
        self.PublicMethod.Log("Start to format data received from serial port, the input data is:{}".format(data))

        nDataLen = len(data)
        if(nDataLen == 0):
            self.PublicMethod.Log("The input data is empty, so return empyt")
            return b''

        # 在数据外增加头尾，因此需要确认长度
        nContentDataLen = nDataLen + 4

        # 加密数据的长度，必须是16的倍数
        if nContentDataLen %16 == 0:
            nEnDataLen = nContentDataLen
        else:
            nEnDataLen = nContentDataLen + 16 - nContentDataLen % 16

        self.PublicMethod.Log("The length of the data is:{}, and the Encrypt data length is:{}".format(nDataLen,nEnDataLen))

        # 定义要发送给服务器数据
        bArrDataToServer = bytearray(nEnDataLen)
        bArrDataToServer[0] = self.SysConfig.TimeSequence % 0x100
        bArrDataToServer[1] = int(self.SysConfig.TimeSequence / 0x100 % 0x100)

        # 将数据拷贝到发送给服务器的数组中
        dataIndex = 0
        while dataIndex < nDataLen:
            bArrDataToServer[dataIndex + 2] = data[dataIndex]
            dataIndex = dataIndex + 1

        # 生成校验码
        checkCode = self.PublicMethod.CalCheckCode(bArrDataToServer, 0, nDataLen + 2)
        self.PublicMethod.Log("Calculate CheckCode for data send to server, and the CheckCode={}".format(checkCode))

        # 将校验码经过计算后放在正文的后面
        bArrDataToServer[nContentDataLen - 2] = checkCode % 0x100
        bArrDataToServer[nContentDataLen - 1] = int(checkCode / 0x100)

        bs = 16
        padding = bs - nContentDataLen % bs

        dataIndex = nContentDataLen
        while dataIndex < nEnDataLen:
            bArrDataToServer[dataIndex] = int(padding)
            dataIndex += 1


        # self.PublicMethod.Log("Before encrypt, the data is:{}".format(bArrDataToServer))

        enData = self.Aes.EnCrypt(bytes(bArrDataToServer))

        # self.PublicMethod.Log("After encrypt the data is:{}".format(self.PublicMethod.BytesToHex(enData)))

        nPackDataLen = nEnDataLen + 16
        packData = bytearray(nPackDataLen)

        packData[0] = 0xA5
        packData[1] = 0xA5
        packData[2] = int(nPackDataLen % 0x100)
        packData[3] = int(nPackDataLen / 0x100 % 0x100)
        packData[4] = int(nPackDataLen / 0x10000 % 0x100)
        packData[5] = int(nPackDataLen / 0x1000000 % 0x100)

        packData[6] = int(self.SysConfig.TerminalID % 0x100)
        packData[7] = int(self.SysConfig.TerminalID / 0x100 % 0x100)
        packData[8] = int(self.SysConfig.TerminalID / 0x10000 % 0x100)
        packData[9] = int(self.SysConfig.TerminalID / 0x1000000 % 0x100)

        packData[10] = 0x00
        packData[11] = 0x10

        dataIndex = 0
        while dataIndex < nEnDataLen:
            packData[dataIndex+12] = enData[dataIndex]
            dataIndex += 1

        # self.PublicMethod.Log("Package data send to server, the data is:{}".format(self.PublicMethod.BytesToHex(packData)))

        # self.PublicMethod.Log("Start to checkcode for Package to server")

        outCheckCode = self.PublicMethod.CalCheckCode(packData,2,nPackDataLen - 6)

        self.PublicMethod.Log("CheckCode for Package is:{}".format(outCheckCode))

        packData[nPackDataLen - 4] = int(outCheckCode % 0x100)
        packData[nPackDataLen - 3] = int(outCheckCode / 0x100)
        packData[nPackDataLen - 2] = 0xAA
        packData[nPackDataLen - 1] = 0x55

        return packData

    # 反格式化从服务器获得的数据，形成真正的原始信息
    def UnFormatData(self, dataFromServer):
        nDataLen = len(dataFromServer)
        self.PublicMethod.Log("Data length from server:{}".format(nDataLen))
        if nDataLen <= 20:
            return b''
        # 报文最前面两个字节是否为指定字符
        if dataFromServer[0] != 0xA5 or dataFromServer[1] != 0xA5:
            return b''
        # 报文阶位是否为指定字符
        if dataFromServer[nDataLen -2] != 0xAA or dataFromServer[nDataLen - 1] != 0x55:
            return b''
        # 获取数据长度
        nEnDataLen = dataFromServer[2] + dataFromServer[3] * 0x100 + dataFromServer[4] * 0x10000 + dataFromServer[5] * 0x1000000
        if nDataLen != nEnDataLen:
            return b''
        self.PublicMethod.Log("Real data len:{}".format(nEnDataLen))
        nTerminalID = dataFromServer[6] + dataFromServer[7] * 0x100 + dataFromServer[8] * 0x10000 + dataFromServer[9] * 0x1000000
        nMsgVersion = dataFromServer[10] + dataFromServer[11] * 0x100
        self.PublicMethod.Log("TerminalID:{}\tMsgVersion:{}".format(nTerminalID,nMsgVersion))
        if nMsgVersion != 0x1000:
            return b''

        # 获得校验码信息
        nOutCheckCode = (dataFromServer[nDataLen - 4] + dataFromServer[nDataLen - 3] * 0x100)

        if nOutCheckCode != 0:
            # 根据报文生成校验码
            nOutCheckCodeCal = self.PublicMethod.CalCheckCode(dataFromServer, 2, nDataLen - 6)
            self.PublicMethod.Log("CheckCode in protocol is {}, and the CheckCode calculated is {}".format(nOutCheckCode,nOutCheckCodeCal))
            # print("Out CheckCode in package:",nOutCheckCode,"\tOut Checkcode cal:",nOutCheckCodeCal)
            if nOutCheckCode != nOutCheckCodeCal:
                self.Logger.error("CheckCode DOES NOT matched")
                print('Not matched')
                return dataFromServer

        dataToDeCrypt = dataFromServer[12:nDataLen -4]
        nDataToDeCryptLen = len(dataToDeCrypt)

        dataDecrypt = self.Aes.DeCrypt(dataToDeCrypt)

        nDataDecryptLen = len(dataDecrypt)

        nTimeSequence = dataDecrypt[0] + dataDecrypt[1] * 0x100

        nIndex = 0
        while nIndex < len(dataDecrypt):
            if dataDecrypt[nIndex:nIndex+8] == b'ErrorID\t':
                break
            else:
                nIndex += 1

        nCheckCodeInMsg = (dataDecrypt[nDataDecryptLen -2] + dataDecrypt[nDataDecryptLen - 1] * 0x100)

        if nCheckCodeInMsg != 0:
            nCheckCodeCal = self.PublicMethod.CalCheckCode(dataDecrypt,0,len(dataDecrypt) - 2)

        byteError = dataDecrypt[nIndex:nIndex+9]

        if byteError == b'ErrorID\t0':
            return 0
        else:
            print("ErrorInfo:", dataToDeCrypt[nIndex+9:nIndex+30])
            return 1
        # return dataDecrypt

    # 开始程序运行，接收串口数据
    def Start(self):
        self.PublicMethod.Log("Start serial port thread to receive data")
        self.PublicMethod.Log("Start thread which process data received from serial ports")
        for th in self.DataProcessThreads:
            th.start()

    # 上传数据
    def SynchronizeChem(self):
        lstModifiedChem = self.Sqlite.GetChemCode()
        if len(lstModifiedChem) == 0:
            return

        curTime = time.strftime("%Y%m%d%H%M%S000")
        strMsg = "TableName\tSYS_InstrumentChem\rChangeTime\t" + curTime + "\rTableData\tInstrumentID\tChemID\tTestItem\r\tSN\tSN\tSN\r"
        for chemItem in lstModifiedChem:
            itemInfo = "\t" + chemItem.InstrumentName + "\t" + chemItem.ChemCode + "\t" + chemItem.TestItemCode + "\r"
            strMsg = strMsg + itemInfo

        strMsg = strMsg + "MessageID\tUploadSystemTable\r"
        self.PublicMethod.Log(strMsg)
        bMsg = strMsg.encode(encoding='utf-8')
        encryData = self.FormatComData(bMsg)
        dataRecv = self.Client.SendDataToServer(encryData)
        nErrorID = self.UnFormatData(dataRecv)
        if nErrorID == 0:
            print('Upload chemitem ok')
        else:
            print('Upload chemitem failed')

    def StateQuery(self):
        bMsg = b'MessageID\tQueryState\r'
        encryData = self.FormatComData(bMsg)
        dataRecv = self.Client.SendDataToServer(encryData)
        nErrorID = self.UnFormatData(dataRecv)
        if nErrorID == 0:
            print('QueryState OK')
        else:
            print('Query state failed')

    # 仪器信息
    def SynchronizeInstrInfo(self):
        lstInstr = self.Sqlite.GetInstrumentInfoFromDB()
        if len(lstInstr) == 0:
            return

        curTime = time.strftime("%Y%m%d%H%M%S000")
        strMsg = "TableName\tSYS_InstrumentInfo\r"
        strMsg = strMsg + "ChangeTime\t" + curTime +"\r"
        strMsg = strMsg + "TableData\tInstrumentID\tInstrumentName\tInstrumentSN\tInstrumentLocate\tDisableFlag\tHighIDRange\tMidIDRange\tLowIDRange\tLastModifyTime\r"
        strMsg = strMsg + "\tSN\tSN\tSN\tSN\tBN\tSN\tSN\tSN\tSN\r"

        for instr in lstInstr:
            instrData = "\t" + instr.InstrumentID + "\r" + instr.InstrumentName + "\r" + instr.InstrumentSerialNo + "\r" + instr.InstrumentLocation + "\r"
            if instr.IsActive:
                instrData = instrData + "1\t"
            else:
                instrData = instrData + "0\t"

            instrData = instr.HighConcentrationID + "\t" + instr.MidConcentrationID + "\t" + instr.LowConcentrationID + "\t" + curTime + "\r"
            strMsg = strMsg + instrData

        strMsg = strMsg + "MessageID\tUploadSystemTable\r"

        self.PublicMethod.Log(strMsg)


if __name__ == "__main__":
    eqap = EQAPBox()
    eqap.Start()

    # sqlite = SqliteHelper('/home/projects/EQAP/DB/Eqap.DB')
    # sqlite = SqliteHelper('./DB/Eqap.DB')


    # sqlite.ExecuteSqlCmd('''ALTER TABLE BSC_InstrumentInfo ADD COLUMN InstrumentID NVARCHAR(128)''')
    # sqlite.ExecuteSqlCmd('''UPDATE BSC_InstrumentInfo SET InstrumentID = InstrumentName ''')

    # print(sqlite.CleanCommDataFromDB(5))
    # sqlite.ExecuteSqlCmd("ALTER TABLE BSC_SysConfig ADD COLUMN RetryTims INT")
    # sqlite.ExecuteSqlCmd('''UPDATE BSC_SysConfig SET LastDataCleanDate = '2020/07/01' ''')
    #
    # commData = sqlite.GetCommDataFromDB(10)
    # for data in commData:
    #     print('ssss',data.CreateTime)

    # sqlite.ExecuteSqlCmd("DROP TABLE WOR_EqapCommInfo")
    # sqlite.ExecuteSqlCmd('''ALTER TABLE BSC_SysConfig ADD COLUMN LastDataCleanDate NVARCAR(32)''')
    # sqlite.ExecuteSqlCmd('''UPDATE BSC_SysConfig SET DataKeptDays = 3''')
    # curTime = datetime.datetime.now().date()
    # strCurTime = curTime.strftime("%y-%m-%d")
    # print(strCurTime)
    # sqlite.ExecuteSqlCmd('''UPDATE BSC_SysConfig SET LastDataCleanDate = '{}' '''.format(strCurTime))

    # sqlite.ExecuteSqlCmd('''UPDATE BSC_DeviceInfo SET ServerIP = '122.144.182.35',ServerPort = 6433 ''')

    # sqlite.ExecuteSqlCmd('''DROP TABLE WOR_EqapCommInfo''')

    # sqlite.ExecuteSqlCmd('''SELECT SerialNo, DetailedInfo,IsUploaded, ProtocolID,InstrumentName, RetryTimes FROM WOR_EqapCommInfo WHERE IsUploaded = 0 ORDER BY SerialNo asc LIMIT 10''')
    # instrs = sqlite.GetInstrumentInfoFromDB()
    # for instr in instrs:
    #     print(instr.InstrumentID, instr.InstrumentName,instr.InstrumentSerialNo,instr.InstrumentDesc,instr.InstrumentLocation,instr.HighConcentrationID,instr.MidConcentrationID,instr.LowConcentrationID,instr.ProtocolID,instr.BaudRate,instr.PortName,instr.IsActive)
    # sqlite.SaveInstrumentInfoToDB(('AU5800-2','AU5800-2_SerialNo','AU5800-2_Desc','AU5800-2_Location','AU5800-2_H_ContentID','AU5800-2_M_ContentID','AU5800-2_L_ContentID',1,9600,'com5',True))

    # #/dev/ttyXRUSB0
    # #/dev/ttyXRUSB0
    # sqlite.ExecuteSqlCmd('''UPDATE  BSC_InstrumentInfo SET PortName = '/dev/tty',IsActive = True WHERE InstrumentSerialNo = 'AU5800-1_SerialNo' ''')

    # sqlite.ExecuteSqlCmd('''DELETE FROM BSC_InstrumentInfo WHERE InstrumentSerialNo = 'AU5800-2_SerialNo' ''')

    # print(sqlite.GetDeviceInfoFromDB().DeviceName)

    # lst = sqlite.GetProtocolMsgInfo()
    # for m in lst:
    #     print(m.MsgID,m.MsgTypeID,m.SampleIDFrom)

    # sqlite.ExecuteSqlCmd("UPDATE BSC_InstrumentInfo SET InstrumentName ='ITC98_1' WHERE InstrumentName = 'AU5800-2'")
    # print(sqlite.GetInstrumentInfoFromDB()[0].PortName)
    # model = QCSamlpeInfo()
    # model.QCSampleNo = "1001"
    # model.QCSampleType = "H"
    # model.InstrumentNo = 1
    # sqlite.SaveQCSampleInfo(model)
    #
    # lst = sqlite.GetQCSampleInfo()
    # print(len(lst))

    # sqlite.ExecuteSqlCmd("Delete from WOR_EqapCommInfo")
    #
    # lstData = sqlite.GetCommDataFromDB(10)
    # print(len(lstData))
    # print(lstData[0].InstrumentName)

    # lst = sqlite.GetProtocolMsgFieldInfo()
    # for model in lst:
    #     print(model.FieldID, model.ProtocolID,model.MsgID,model.FieldName,model.FieldIndex,model.StartPos,model.FieldLen,model.FieldType,model.ValueRange,model.ToBeCleared,model.IsFixed,model.IsRepeat,model.IsUpload)
    # #
    # sqlite.ExecuteSqlCmd("Update BSC_BasicProtocolFieldInfo SET IsUpload = 0 WHERE FieldID = 6")
    #

    # model = ProtocolMsgFieldInfo()
    # model.ProtocolID = 1
    # model.MsgID = 1
    # model.FieldName = 'TestItem'
    # model.FieldIndex = -1
    # model.StartPos = 9
    # model.FieldLen = 2
    # model.FieldType = 'SN'
    # model.ValueRange = ''
    # model.ToBeCleared = 0
    # model.IsFixed = 0
    # model.IsRepeat = 1
    # nFieldIndex = sqlite.SaveProtocolMsgFieldInfo(model)
    # print(nFieldIndex)

    # sqlite.ExecuteSqlCmd('DROP TABLE BSC_BasicProtocolFieldInfo')
    # sqlite.ClearCommDataFromDB()


    # sqlite.InsertChemCode(('046', 'MALB'))
    # sqlite.InsertChemCode(('097', 'NA'))
    # sqlite.InsertChemCode(('099', 'CL'))
    # sqlite.InsertChemCode(('017', 'CA'))
    # sqlite.InsertChemCode(('019', 'MG'))
    # sqlite.InsertChemCode(('018', 'P'))
    # sqlite.InsertChemCode(('005', 'TP'))
    # sqlite.InsertChemCode(('006', 'ALB'))
    # sqlite.InsertChemCode(('003', 'TBIL-C'))
    # sqlite.InsertChemCode(('004', 'DBIL-C'))
    # sqlite.InsertChemCode(('002', 'ALT'))
    # sqlite.InsertChemCode(('001', 'AST'))
    # sqlite.InsertChemCode(('007', 'GGT'))
    # sqlite.InsertChemCode(('008', 'ALP'))
    # sqlite.InsertChemCode(('020', 'TBA'))
    # sqlite.InsertChemCode(('025', 'PA'))
    # sqlite.InsertChemCode(('009', 'UREA'))
    # sqlite.InsertChemCode(('010', 'CRE'))
    # sqlite.InsertChemCode(('012', 'GLU'))
    # sqlite.InsertChemCode(('011', 'UA'))
    # sqlite.InsertChemCode(('013', 'CHO'))
    # sqlite.InsertChemCode(('014', 'TG'))
    # sqlite.InsertChemCode(('022', 'HDL'))
    # sqlite.InsertChemCode(('023', 'LDL'))
    # sqlite.InsertChemCode(('024', 'LP(A)'))
    # sqlite.InsertChemCode(('015', 'CK'))
    # sqlite.InsertChemCode(('016', 'LDH'))
    # sqlite.InsertChemCode(('029', 'HBDH'))
    # sqlite.InsertChemCode(('028', 'CKMB'))
    # sqlite.InsertChemCode(('033', 'FE'))
    # sqlite.InsertChemCode(('034', 'TRF'))
    # sqlite.InsertChemCode(('041', 'IG-A'))
    # sqlite.InsertChemCode(('043', 'IG-M'))
    # sqlite.InsertChemCode(('042', 'IG-G'))
    # sqlite.InsertChemCode(('044', 'C3'))
    # sqlite.InsertChemCode(('045', 'C4'))
    # sqlite.InsertChemCode(('048', 'ASO'))
    # sqlite.InsertChemCode(('026', 'B2-MG'))
    # sqlite.InsertChemCode(('032', 'CYS-C'))

    # sqlite.InsertChemCode(('047', 'RF'))
    #
    # lstChem = sqlite.GetChemCode()
    # for chemItem in lstChem:
    #     print(chemItem.ChemCode,chemItem.TestItemCode)

    # print(sqlite.ExecuteSqlCmd('''UPDATE BSC_ChemCode SET TestItemCode = 'CHOL' WHERE ChemCode = '013' '''))


    # msg = "InstrumentList\tITC98_1\rTableData\tInstrumentID\tTimeID\tSampleID\tChemID\tTestItem\tTestTime\tTestValue\tQC_Type\tQC_SN\tQC_ValidDate\tRG_SN1\tRG_SN2\tRG_SN3\tRG_SN4\r\tSN\tSN\tSN\tSN\tSN\tSN\tSN\tSN\tSN\tSN\tSN\tSN\tSN\tSN\r\tITC98_1\t2020/06/18 14:22:24\t9984\t098\tK\t2020/06/18 14:22:24\t6.39\tH\t\\\t\\\t9999.9999\t\\\t\\\t\\\rMessageID\tUploadQCTestResult\r"
    # encodeMsg = msg.encode(encoding='utf-8')
    # enMsg = eqap.FormatComData(encodeMsg)
    # print("Endata len:",len(enMsg),len(msg))
    # index = 0
    # for e in enMsg:
    #     print(index,enMsg[index])
    #     index += 1



