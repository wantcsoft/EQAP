import sqlite3
import os
import datetime
from PublicMethods import PublicMethods
from Models.SysConfigInfoModel import SysConfigInfo
from Models.CommDataModel import CommDataModel
from Models.DeviceInfoMode import DeviceInfoModel
from Models.InstrumentInfoModel import InstrumentInfoModel
from Models.ChemCodeModel import ChemCodeInfo
from Models.QCSampleSetupInfoModel import QCSamlpeSetupInfo

from Protocol.ProtocolInfo import ProtocolInfo
from Protocol.ProtocolMsgInfoModel import ProtocolMsgInfo
from Protocol.ProtocolMsgFieldInfoModel import ProtocolMsgFieldInfo

# Sqlite 操作类，完成所有的数据库操作
# 1、创建数据库架构
# 2、将数据保存到数据库中
# 3、从数据库提取数据，获得所有未发送到服务端数据
# 4、删除数据，在数据发送到服务器成功后，会根据数据库记录的序号删除对应的数据，避免重复发送。

class SqliteHelper:
    # 设置默认的数据库文件路径，如果路径不存在，则直接创建对应的路径
    def __init__(self,strDBFileName):
        if strDBFileName == '':
            self.DbFileName = './DB/Eqap.DB'
        else:
            self.DbFileName = strDBFileName

        dbFilePath = os.path.split(self.DbFileName)[0]
        if not os.path.exists(dbFilePath):
            os.mkdir(dbFilePath)


        self.CreateDatabaseScheame()


    # 创建数据库结构，在数据库不存在的情况下
    '''
    创建数据库结构
    表： 
        WOR_EqapCommInfo            通讯数据表，数据缓存
        BSC_DeviceInfo              设备表，Box设备信息，包括服务器IP等信息
        BSC_InstrumentInfo          仪器表，检测设备信息，包括通讯端口的设置信息
        BSC_ProtocolInfo            报文表，报文的基础信息定义
        BSC_ProtocolMsgInfo         报文消息分类表，只解析对应报文中已经定义的消息，未定义的消息全部放弃。
        BSC_BasicProtocolFieldInfo  报文消息字段表，每个报文中消息对应的字段设置信息
        BSC_ChemCode                通道号与测试项目转换表
        BSC_QCSample                指控样本设置
    '''
    def CreateDatabaseScheame(self):
        conn = sqlite3.connect(self.DbFileName)
        cursor = conn.cursor()

        # 创建基础配置信息表
        '''
        SaveLog：是否保存日志
        TerminalID：终端ID
        TimeSequence：时序
        '''
        sqlCreteSysConfigTable = '''CREATE TABLE IF NOT EXISTS BSC_SysConfig
        (
            SaveLog         INT,
            TerminalID      INT,
            TimeSequence    INT,
            RetryTimes      INT,
            DataKeptDays    INT,
            LastDataCleanDate   NVARCHAR(32)
        )
        '''
        cursor.execute(sqlCreteSysConfigTable)


        # 创建结果表，如果表已经存在，则没有任何动作
        '''
        SerialNo 是序列号，代表接收的顺序。
        DetailedInfo 报文的详细内容。
        IsUploaded 标识报文是否以上传，以上传的信息会定期进行清除
        '''
        sqlCreateCommInfoTable = '''CREATE TABLE IF NOT EXISTS WOR_EqapCommInfo
        (
            SerialNo        INTEGER PRIMARY KEY AUTOINCREMENT,
            DetailedInfo    NVARCHAR(2048),
            IsUploaded      INT,
            ProtocolID      INT,
            RetryTimes      INT,
            InstrumentName  NVARCHAR(128),
            CreateTime      DATE 
        );
        '''
        cursor.execute(sqlCreateCommInfoTable)

        # 创建终端设备数据表，即Box本身的信息，同时包括设备所连接的服务器信息
        '''
        DeviceID 自增长列，保存设备的序号
        DeviceName 设备名称
        DeviceSerialNo 设备序列号
        DeviceLocation 设备位置信息
        ServiceIP 连接的服务器地址
        ServerPort 连接的服务器端口号
        '''
        sqlCreateDeviceTable = '''CREATE TABLE IF NOT EXISTS BSC_DeviceInfo
        (
            DeviceID        INTEGER PRIMARY KEY AUTOINCREMENT,
            DeviceName      NVARCHAR(128),
            DeviceSerialNo  NVARCHAR(128),
            DeviceDesc      NVARCHAR(128),
            DeviceLocation  NVARCHAR(128),
            ServerIP        NVARCHAR(128),
            ServerPort      INT,
            TimeOut         FLOAT 
        );'''
        cursor.execute(sqlCreateDeviceTable)

        # 仪器信息，实验室检测设备信息，查询的时候会对仪器设备进行过滤性提取，只提取启用的设备，并且进行合理性校验
        '''
        InstrumentNo 仪器的序号，唯一标识
        InstrumentName 仪器名称，测试设备名称
        InstrumentSerialNo 仪器的序列号
        InstrumentDesc 仪器的备注信息
        InstrumentLocation 仪器的位置
        HighConcentrationID 高浓度ID
        MidConcentrationID 中浓度ID
        LowConcentrationID 低浓度ID
        ProtocolID 使用的报文编号
        BaudRate 串口的波特率
        PortName 串口名称
        IsActive 是否启用
        '''
        sqlCreateInstrumentInfoTable = '''CREATE TABLE IF NOT EXISTS BSC_InstrumentInfo
        (
            InstrumentNo        INTEGER PRIMARY KEY AUTOINCREMENT,
            InstrumentID        NVARCHAR(128),
            InstrumentName      NVARCHAR(128),
            InstrumentSerialNo  NVARCHAR(128),
            InstrumentDesc      NVARCHAR(128),
            InstrumentLocation  NVARCHAR(128),
            HighConcentrationID NVARCHAR(128),
            MidConcentrationID  NVARCHAR(128),
            LowConcentrationID  NVARCHAR(128),
            ProtocolID          INTEGER,
            BaudRate            INT,
            PortName            NVARCHAR(128),
            IsActive            INT
        )'''
        cursor.execute(sqlCreateInstrumentInfoTable)

        # 创建协议表，存储协议的基础信息，例如序号，名称，类型信息暂时不确定
        '''
        ProtocolID 报文的编号，唯一识别表值
        ProtocolName 报文的名称，用于显示
        ProtocolType 报文的类型
        IsEnabled 是否启用
        '''
        sqlCreateProtocolInfoTable = '''CREATE TABLE IF NOT EXISTS BSC_ProtocolInfo
        (
            ProtocolID      INTEGER PRIMARY KEY AUTOINCREMENT,
            ProtocolName    NVARCHAR(256),
            ProtocolType    NVARCHAR(64),
            IsEnabled       INT
        )
        '''
        cursor.execute(sqlCreateProtocolInfoTable)

        # 存储协议中不同类型的报文，例如 Order(医嘱信息)、Result(结果，仪器上传)、Query(编程请求，仪器请求)、Program(编程下载，仪器接收)
        # 消息对应的报文，每个报文可以存在多种类型的消息，消息的定义包括报文头、结束符、报文内容的数量等信息，定义了对应消息上传的格式
        '''
        MsgID 报文对应信息的ID，与ProtocolID组成唯一标识
        ProtocolID 报文编号，与 BSC_ProtocolInfo 中的 ProtocolID关联
        ProtocolMsgType 消息类型，例如 1 表示病人信息
        MsgHeader 消息头，例如 P标识病人信息，与消息类型配合使用
        MsgEndFlag 消息尾，用于判断消息是否完整，如果为 ‘’ 则不判断
        FieldCount 消息字段的数量，其中多个结果信息作为一个字段看待。
        UploadFormat 消息上传的格式。
        NeedToUpload 是否需要上传到服务器
        '''
        sqlCreateProtocolMsgTable = '''CREATE TABLE IF NOT EXISTS BSC_ProtocolMsgInfo
        (
            MsgID           INTEGER PRIMARY KEY AUTOINCREMENT,
            ProtocolID      INTEGER,
            ProtocolMsgType INTEGER,            
            MsgHeader       NVARCHAR(32),
            MsgEndFlag      NVARCHAR(32),
            FieldCount      INTEGER,
            UploadFormat    NVARCHAR(1024),
            ToBeUpload      INT,
            SampleIDFrom    NVARCHAR(128)
        )
        '''
        cursor.execute(sqlCreateProtocolMsgTable)

        # 报文中不同类型信息的全部字段设置，其中FieldIndex 与StartPos， Len冲突，针对不同类型的报文，例如存在分隔符的报文使用FieldIndex，无分隔符的使用起始位置加长度
        '''
        ProtocolID 协议ID
        MsgID 消息的ID
        FieldID 字段的ID
        FieldName 字段的名称，在上传时会将字段名称上传
        FieldType 字段类型， 在上传时会附带字段的类型
        FieldIndex 字段所在位置，存在分隔符的情况下
        StartPos 字段的起始位置，从0开始计算
        FieldLen 字段长度
        ValueRange 取值范围限制，可以对报文中的信息进行校验
        ToBeCleared 是否小清洗，>0 表示要清洗， 0：不清洗
        '''
        sqlCreateBasicProtocolFieldInfoTable = '''CREATE TABLE IF NOT EXISTS BSC_BasicProtocolFieldInfo
        (
            FieldID         INTEGER PRIMARY KEY AUTOINCREMENT,
            ProtocolID      INTEGER,
            MsgID           INTEGER,            
            FieldName       NVARCHAR(128),
            FieldType       NVARCHAR(32),
            FieldIndex      INT,
            StartPos        INT,
            FieldLen        INT,
            ValueRange      NVARCHAR(256),
            ToBeCleared     INT,
            IsRepeat        INT,
            IsUpload        INT
        )
        '''
        cursor.execute(sqlCreateBasicProtocolFieldInfoTable)

        '''
        ChemCode        通道号
        TestItemCode    测试项目代码
        '''
        sqlCreateBasicChemCodeTransTable = '''CREATE TABLE IF NOT EXISTS BSC_ChemCode
        (
            ChemCode        NVARCHAR(128) PRIMARY KEY ,
            TestItemCode    NVARCHAR(128)
        )
        '''
        cursor.execute(sqlCreateBasicChemCodeTransTable)

        '''
        BSC_QCSample        
        '''
        sqlCreateQCSampleInfoTable = '''CREATE TABLE IF NOT EXISTS BSC_QCSampleInfo
        (
            QCSampleNo      NVARCHAR(32),
            QCSampleType    NVARCHAR(16),
            InstrumentNo    INT
        )
        '''
        cursor.execute(sqlCreateQCSampleInfoTable)


        '''
        WOR_ErrorInfo
        '''
        sqlCreateErrorInfoTable = '''CREATE TABLE IF NOT EXISTS WOR_ErrorInfo
        (
            MessageID           NVARCHAR(32),
            MessageTime         NVARCHAR(32),
            ErrorInfo           NVARCHAR(128)
        )'''
        cursor.execute(sqlCreateErrorInfoTable)

        cursor.close()
        conn.commit()
        conn.close()
        return True


    def SaveSysConfig(self,nSaveLog,nTerminalID,nTimeSequence,nRetryTims,nDataKeptDays,dtLastCleanDate):
        sqlCmdTxt = "INSERT INTO BSC_SysConfig(SaveLog,TerminalID,TimeSequence,RetryTims,DataKeptDays)VALUES({},{},{},{})".format(nSaveLog,nTerminalID,nTimeSequence,nDataKeptDays)
        conn = sqlite3.connect(self.DbFileName)
        conn.execute(sqlCmdTxt)
        conn.commit()
        conn.close()

    def UpdateSysConfig(self,nSaveLog,nTerminalID,nTimeSequence,nRetryTims,nDataKeptDays,dtLastCleanDate):
        sqlCmdTxt = "UPDATE BSC_SysConfig SET SaveLog = {}, TerminalID = {}, TimeSequence = {}, RetryTims = {},DataKeptDays={},LastDataCleanDate='{}'".format(nSaveLog,nTerminalID,nTimeSequence,nRetryTims,nDataKeptDays,dtLastCleanDate)
        conn = sqlite3.connect(self.DbFileName)
        conn.execute(sqlCmdTxt)
        conn.commit()
        conn.close()

    def GetSysConfig(self):
        sqlCmdTxt = '''SELECT SaveLog,TerminalID,TimeSequence,RetryTimes,DataKeptDays,LastDataCleanDate FROM BSC_SysConfig'''
        conn = sqlite3.connect(self.DbFileName)
        result = conn.execute(sqlCmdTxt).fetchone()

        if result is None:
            return SysConfigInfo(0,0,0,0,7,'2000-01-01')
        else:
            return SysConfigInfo(result[0],result[1],result[2],result[3],result[4],result[5])


    # 保存通讯信息
    '''
    保存通讯数据到数据库
    参数：data 
        为数据对象，分为两部分，在传递参数的时候使用 (A,B)
        其中 A 表示通讯数据， B表示上传状态
    返回值：SerialNo
        即插入数据库后生成的自增长序列号，唯一标示对应的数据，在上传到服务器后，可以通过对应额标示对通讯数据进行删除
    '''
    def SaveCommDataToDB(self,data):
        bRetValue = False
        try:
            conn = sqlite3.connect(self.DbFileName)
            cursor = conn.cursor()
            sqlCmdInsert = '''INSERT INTO WOR_EqapCommInfo(DetailedInfo,IsUploaded,ProtocolID,InstrumentName,RetryTimes,CreateTime)VALUES(?,?,?,?,?,?)'''
            # sqlCmdGetSerialNo = '''SELECT SerialNo FROM WOR_EqapCommInfo ORDER BY SerialNo DESC limit 1'''
            cursor.execute(sqlCmdInsert,data)
            cursor.close()
            conn.commit()

            # cursor = conn.cursor()
            # nSerialNo = cursor.execute(sqlCmdGetSerialNo).fetchone()[0]
            bRetValue = True
        except BaseException as e:
            self.Logger.error("Save communication data to DB with Exception:".format(e))
        finally:
            cursor.close()
            conn.commit()
            conn.close()

        return bRetValue

    def UpdateResendTimes(self,nSerialNo,nTimes,nIsUploaded):
        bRetValue = False
        sqlCmdTxt = '''UPDATE WOR_EqapCommInfo SET RetryTimes = {},IsUploaded = {} WHERE SerialNo={}'''.format(nTimes,nIsUploaded,nSerialNo)
        try:
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmdTxt)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            print("Update comm data status failed")
        finally:
            conn.close()
        return bRetValue


    # 提取通讯信息
    '''
    参数：
        nMaxRowCount,获取记录的最大数量，如果设置的参数  <= 0 则获得100条记录
    返回值：
        未上传的通讯数据列表
    '''
    def GetCommDataFromDB(self,nMaxRowCount,nRetryTimes):
        result = []

        if nMaxRowCount <= 0:
            sqlCmdQuery = '''SELECT SerialNo, DetailedInfo,IsUploaded, ProtocolID,InstrumentName, RetryTimes,CreateTime FROM WOR_EqapCommInfo WHERE IsUploaded = 0 and RetryTimes < {maxReTryTimes} ORDER BY SerialNo asc LIMIT 100'''.format(maxReTryTimes = nRetryTimes)
        else:
            sqlCmdQuery = '''SELECT SerialNo, DetailedInfo,IsUploaded, ProtocolID,InstrumentName, RetryTimes,CreateTime FROM WOR_EqapCommInfo WHERE IsUploaded = 0 and RetryTimes < {maxReTryTimes}  ORDER BY SerialNo asc LIMIT {rowCount}'''.format(rowCount=nMaxRowCount,maxReTryTimes = nRetryTimes)

        conn = sqlite3.connect(self.DbFileName)
        cursor = conn.cursor()
        try:
            cursor.execute(sqlCmdQuery)
            rList = cursor.fetchall()
            if len(rList) > 0:
                for r in rList:
                    model = CommDataModel()

                    model.InitializeInfo(r[0],r[1],r[2],r[3],r[4],r[5],r[6])
                    result.append(model)
        except BaseException as e:
            # self.Logger.error("Get communication data from DB with EXCEPTION:".format(e))
            print("Get communication data from DB with EXCEPTION:".format(e))
        finally:
            cursor.close()
            conn.close()

        return result

    # 从数据库中删除通讯数据
    '''
    参数：
        nSerialNo：通讯数据对应的序列号，删除对应的记录信息。
    返回值：
        True：删除成功
        False：删除失败
    '''
    def RevmoeCommDataFromDB(self,nSerialNo):
        bRetValue = False
        try:
            sqlCmd = '''DELETE FROM WOR_EqapCommInfo WHERE SerialNo = {}'''.format(nSerialNo)
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmd)
            bRetValue = True
        except BaseException as e:
            self.Logger.error("Delete data from DB with EXCEPTION, the SerialNo is {}".format(nSerialNo))
        finally:
            conn.commit()
            conn.close()
        return bRetValue

    def CleanCommDataFromDB(self,nDataKeptDays):
        bRetValue = False
        try:
            strTime = (datetime.datetime.now() - datetime.timedelta(days= nDataKeptDays)).strftime('%Y/%m/%d')
            sqlCmd = "DELETE FROM WOR_EqapCommInfo WHERE CreateTime < '{}' ".format(strTime)
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmd)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            print("Error")
        finally:
            conn.close()
        return bRetValue
            # sqlCmdTxt = "DELETE FROM WOR_EqapCommInfo WHERE CreateTime < {}".format()

    def ClearCommDataFromDB(self):
        bRetValue = False
        try:
            sqlCmd = '''DELETE FROM WOR_EqapCommInfo'''
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmd)
            bRetValue = True
        except BaseException as e:
            self.Logger.error("Delete data from DB with EXCEPTION, the SerialNo is {}".format(nSerialNo))
        finally:
            conn.commit()
            conn.close()
        return bRetValue

    # 保存终端设备信息
    '''
    保存设备信息到数据库
    参数：
        data：数据对象，以  ()  包含的一组数据，通过  “，” 进行分隔数据
    返回值：
        True：保存数据成功， False：保存数据失败
    '''
    def SaveDeviceInfoToDB(self,data):
        sqlCreateDeviceTable = '''CREATE TABLE IF NOT EXISTS BSC_DeviceInfo
                (
                    DeviceID        INTEGER PRIMARY KEY AUTOINCREMENT,
                    DeviceName      NVARCHAR(128),
                    DeviceSerialNo  NVARCHAR(128),
                    DeviceDesc      NVARCHAR(128),
                    DeviceLocation  NVARCHAR(128),
                    ServerIP        NVARCHAR(128),
                    ServerPort      INT,
                    TimeOut         FLOAT 
                );'''
        sqlCmdInsert = '''INSERT INTO BSC_DeviceInfo(DeviceName,DeviceSerialNo,DeviceDesc,DeviceLocation,ServerIP,ServerPort,TimeOut)VALUES(?,?,?,?,?,?,?);'''
        bRetValue = False
        try:
            conn = sqlite3.connect(self.DbFileName)
            cursor = conn.cursor()
            cursor.execute(sqlCmdInsert, data)
            bRetValue = True
        except BaseException as e:
            self.Logger.error("Save device information to DB with EXCEPTION, the device info is:{}".format(data))
        finally:
            cursor.close()
            conn.commit()
            conn.close()
        return bRetValue

    # 提取终端设备信息
    '''
    从数据库提取设备信息
    参数：无
    返回值：
        设备信息列表
    '''
    def GetDeviceInfoFromDB(self):
        device =DeviceInfoModel()

        sqlCmdQuery = '''SELECT DeviceID,DeviceName,DeviceSerialNo,DeviceDesc,DeviceLocation,ServerIP,ServerPort,TimeOut FROM BSC_DeviceInfo'''
        try:

            conn = sqlite3.connect(self.DbFileName)
            cursor = conn.cursor()
            cursor.execute(sqlCmdQuery)
            result = cursor.fetchone()

            if result is not None:
                device.InitDeviceInfo(result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7])
        except BaseException as e:
            print("Get communication data from DB with EXCEPTION:".format(e))
        finally:
            cursor.close()
            conn.close()

        return device


    # 保存仪器设备信息到数据库
    '''
    参数：
        data：仪器信息，以 () 包含的一组数据， 以 “，” 对数据进行分隔
    返回值：
        True：保存成功， False：保存失败
    '''
    def SaveInstrumentInfoToDB(self,model):
        sqlCmdInsert = '''INSERT INTO BSC_InstrumentInfo(InstrumentID,InstrumentName,InstrumentSerialNo,InstrumentDesc,InstrumentLocation,HighConcentrationID,MidConcentrationID,LowConcentrationID,ProtocolID,BaudRate,PortName,IsActive
        )VALUES(?,?,?,?,?,?,?,?,?,?,?);'''

        bRetValue = False
        try:
            conn = sqlite3.connect(self.DbFileName)
            cursor = conn.cursor()
            cursor.execute(sqlCmdInsert, model)
            bRetValue = True
        except BaseException as e:
            self.Logger.error("Get communication data from DB with EXCEPTION:".format(e))
        finally:
            cursor.close()
            conn.commit()
            conn.close()

        return bRetValue


    # 更新仪器信息
    '''
    参数：
        nInstrNo：           仪器的编号，唯一标识一个仪器
        strInstrName：       设备名称
        strInstrSerialNo：   设备序列号
        strInstrDesc：       设备备注信息
        strInstrLocation：   设备位置
        strHighConcentID：   高浓度标记
        strMidConcentID：    中浓度标记
        strLowConcentID：    低浓度标记
        nProtocolID：        协议ID
        nBaudRate：          波特率
        strPortName：        端口名称
        nIsActive            是否启用
    返回值：
        True：更新成功， False：更新失败
    '''
    def UpdateInstrumentInfoToDB(self,nInstrNo,strInstrID,strInstrName,strInstrSerialNo,strInstrDesc,strInstrLocation,strHighConcentID,strMidConcentID,strLowConcentID,nProtocolID,nBaudRate,strPortName,nIsActive):
        bRetValue = False
        sqlCmdUpdate = '''UPDATE BSC_InstrumentInfo SET InstrumentID = '{}' InstrumentName = '{}', InstrumentSerialNo = '{}', InstrumentDesc = '{}',InstrumentLocation = '{}',HighConcentrationID = '{}',MidConcentrationID = '{}',LowConcentrationID = '{}',ProtocolID = {}, BaudRate = {}, PortName ='{}',IsActive = {} WHERE InstrumentNo = {} '''.format(strInstrName,strInstrSerialNo,strInstrDesc,strInstrLocation,strHighConcentID,strMidConcentID,strLowConcentID,nProtocolID,nBaudRate,strPortName,nIsActive,nInstrNo)
        try:
            conn = sqlite3.connect(self.DbFileName)
            cursor = conn.cursor()
            cursor.execute(sqlCmdUpdate)
            bRetValue = True
        except BaseException as e:
            self.Logger.error("Get communication data from DB with EXCEPTION:".format(e))
        finally:
            cursor.close()
            conn.commit()
            conn.close()
        return bRetValue


    # 从数据库获得仪器信息
    '''
    参数：无
    返回值：
        仪器信息列表
    '''
    def GetInstrumentInfoFromDB(self):
        sqlCmdQuery = '''SELECT InstrumentNo,InstrumentID,InstrumentName,InstrumentSerialNo,InstrumentDesc,InstrumentLocation,HighConcentrationID,MidConcentrationID,LowConcentrationID,ProtocolID,BaudRate,PortName,IsActive FROM BSC_InstrumentInfo'''

        lstInstr = []

        try:
            conn = sqlite3.connect(self.DbFileName)
            cursor = conn.cursor()
            cursor.execute(sqlCmdQuery)
            instrs = cursor.fetchall()

            for instr in instrs:
                model = InstrumentInfoModel()
                model.InitInstrumentInfo(instr[0],instr[1],instr[2],instr[3],instr[4],instr[5],instr[6],instr[7],instr[8],instr[9],instr[10],instr[11],instr[12])
                lstInstr.append(model)

        except BaseException as e:
            self.Logger.error("Get communication data from DB with EXCEPTION:".format(e))
        finally:
            cursor.close()
            conn.close()

        return lstInstr

    # 获得报文列表
    '''
    参数：无
    返回值：
        报文设置信息列表
    '''
    def GetProtocolList(self):
        sqlCmdProtocolQuery = '''SELECT ProtocolID,ProtocolName,ProtocolType,IsEnabled FROM BSC_ProtocolInfo'''

        lstProtocolModel = []

        try:
            conn = sqlite3.connect(self.DbFileName)
            lstProtocol = conn.execute(sqlCmdProtocolQuery).fetchall()

            for prot in lstProtocol:
                protocol = ProtocolInfo()
                protocol.InitProtocolInfo(prot[0],prot[1],prot[2],prot[3])
                lstProtocolModel.append(protocol)
        except BaseException as e:
            self.Logger.error("Get Protocol list from DB with EXCEPTION:".format(e))
        finally:
            conn.close()
        return lstProtocolModel


    # 保存通讯报文信息
    '''
    参数：
        data：报文信息对象
    返回值：
        报文信息的ID，唯一标识报文
    '''
    def SaveProtocolInfo(self, model):
        sqlCmdTxt = '''INSERT INTO BSC_ProtocolInfo(ProtocolName,ProtocolType,IsEnabled)VALUES('{}','{}',{})'''.format(model.ProtocolName,model.ProtocolType,model.IsEnabled)
        sqlCmdProtocolIDQuery = '''SELECT ProtocolID FROM BSC_ProtocolInfo ORDER BY ProtocolID DESC limit 1'''
        nProtocolID = 0

        try:
            conn = sqlite3.connect(self.DbFileName)
            cursor = conn.cursor()
            cursor.execute(sqlCmdTxt)
            cursor.close()
            conn.commit()

            cursor = conn.cursor()
            nProtocolID = cursor.execute(sqlCmdProtocolIDQuery).fetchone()[0]
        except BaseException as e:
            self.Logger.error("Save protocol information to DB with EXCEPTION:{}".format(e))
        finally:
            conn.close()
        return nProtocolID


    # 通过报文的 ProtocolID 更新报文信息
    '''
    参数：
        nProtocolID：报文的ID，唯一标识报文
        strProtocolName：协议名称
        strProtocolType：协议类型
        nIsEnabled：是否启用
    返回值：
        True：更新协议信息到数据库陈宫，False：更新失败
    '''
    def UpdateProtocolInfo(self,model):
        bRetValue = False;

        if nProtocolID <= 0:
            return bRetValue

        try:
            sqlCmdTxt = '''UPDATE BSC_ProtocolInfo SET ProtocolName = '{}',ProtocolType='{}',IsEnabled = {} WHERE ProtocolID = {}'''.format(model.ProtocolName,model.ProtocolType,model.IsEnabled,model.ProtocolID)
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmdTxt)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            self.Logger.error("Update protocol information with EXCEPTION:{}".format(e))
        finally:
            conn.close()

        return bRetValue

    # 保存协议的消息信息到数据库
    '''
    参数：
        data：报文消息的设置信息
    返回值：
        消息的ID
    '''
    def SaveProtocolMsgInfo(self,model):
        msgID = 0

        try:
            sqlSaveCmdTxt = '''INSERT INTO BSC_ProtocolMsgInfo(ProtocolID,ProtocolMsgType,MsgHeader,MsgEndFlag,FieldCount,UploadFormat,ToBeUpload,SampleIDFrom)VALUES({},'{}','{}','{}',{},'{}',{},'{}')'''.format(model.ProtocolID,model.MsgTypeID,model.MsgHeader,model.MsgEnd,model.FieldCount,model.UploadFormat,model.ToBeUpload,model.SampleIDFrom)
            sqlGetIDCmdTxt = '''SELECT MsgID FROM BSC_ProtocolMsgInfo ORDER BY MsgID DESC limit 1'''

            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlSaveCmdTxt)
            conn.commit()

            msgID = conn.execute(sqlGetIDCmdTxt).fetchone()[0]
        except BaseException as e:
            self.Logger.error("Save protocol msg info to DB with EXCEPTION:{}".format(e))
        finally:
            conn.close()

        return msgID

    # 更新协议中消息行的配置信息
    '''
    参数：
        nProtocolID：    协议ID
        nMsgID:         消息ID
        nMsgType:       消息类型
        strMsgHeader:   消息头
        strMsgEnd:      消息尾
        nFieldCount:    字段数量
        strUploadFormat:上传格斯
        nNeedToUpload:  是否需要上传
    '''
    def UpdateProtocolMsgInfo(self,model):
        bRetValue = False

        try:
            sqlCmdTxt = '''UPDATE BSC_ProtocolMsgInfo SET ProtocolMsgType={},MsgHeader='{}', MsgEndFlag = '{}', FieldCount = {}, UploadFormat = '{}', ToBeUpload = {},SampleIDFrom='{}' WHERE ProtocolID = {} AND MsgID = {} '''.format(model.MsgTypeID,model.MsgHeader,model.MsgEnd,model.FieldCount,model.UploadFormat,model.ToBeUpload,model.SampleIDFrom,model.ProtocolID,model.MsgID)

            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmdTxt)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            self.Logger.error("Update protocol msg information with EXCEPTION:{}".format(e))
        finally:
            conn.close()
        return bRetValue

    # 删除报文消息，同时会删除消息本身对应字段的消息
    '''
    参数：
        nProtocolID：报文ID
        nMsgID：     要删除消息ID
    返回值
        True：删除消息设置成功，False：删除失败
    '''
    def RemoveProtocolMsgInfo(self,nProtocolID,nMsgID):
        bRetValue  =False

        try:
            sqlCmdTxt = '''DELETE FROM BSC_ProtocolMsgInfo WHERE ProtocolID = {} AND MsgID = {} '''.format(nProtocolID,nMsgID)
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmdTxt)
            # conn.commit()

            sqlCmdTxt = '''DELETE FROM BSC_BasicProtocolFieldInfo WHERE ProtocolID = {} AND MsgID = {}'''.format(nProtocolID,nMsgID)
            conn.execute(sqlCmdTxt)
            conn.commit()

            bRetValue = True
        except BaseException as e:
            self.Logger.error("Update protocol msg information with EXCEPTION:{}".format(e))
        finally:
            conn.close()
        return bRetValue

    def GetProtocolMsgInfo(self):
        sqlCmdTxt = '''SELECT MsgID,ProtocolID,ProtocolMsgType,MsgHeader,MsgEndFlag,FieldCount,UploadFormat,ToBeUpload,SampleIDFrom FROM BSC_ProtocolMsgInfo'''
        lstProtocolMsg = []
        try:
            conn = sqlite3.connect(self.DbFileName)
            result = conn.execute(sqlCmdTxt).fetchall()

            for r in result:
                model = ProtocolMsgInfo()
                model.InitProtocolMsgInfo(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8])
                lstProtocolMsg.append(model)
        except BaseException as e:
            print("Get Protocol message list from DB with EXCEPTION:".format(e))
        finally:
            conn.close()

        return lstProtocolMsg


    # 保存报文消息的字段信息
    '''
    参数：
        data：保温消息的字段信息
    返回值：
        字段信息的ID
    '''
    def SaveProtocolMsgFieldInfo(self,model):
        nMsgFieldID = 0
        try:
            sqlSaveCmdTxt = ''' INSERT INTO  BSC_BasicProtocolFieldInfo(ProtocolID,MsgID,FieldName,FieldType,FieldIndex,StartPos,FieldLen,ValueRange,ToBeCleared,IsFixed,IsRepeat,IsUpload)VALUES({},{},'{}','{}',{},{},{},'{}',{},{},{},{})'''.format(model.ProtocolID,model.MsgID,model.FieldName,model.FieldType,model.FieldIndex,model.StartPos,model.FieldLen,model.ValueRange,model.ToBeCleared,model.IsFixed,model.IsRepeat,model.IsUpload)
            sqlSerialNoGetCmdTxt = '''SELECT FieldID FROM BSC_BasicProtocolFieldInfo ORDER BY FieldID DESC limit 1'''
            conn = sqlite3.connect(self.DbFileName)

            conn.execute(sqlSaveCmdTxt)
            conn.commit()

            nMsgFieldID = conn.execute(sqlSerialNoGetCmdTxt).fetchone()[0]
        except BaseException as e:
            self.Logger.error("Save protocol msg field info to DB with EXCEPTION:{}".format(e))
        finally:
            conn.close()

        return nMsgFieldID


    # 更新报文信息中的字段信息
    '''
    参数：
        nProtocolID：    协议ID
        nMsgID：         消息ID
        nFieldID：       字段ID
        strFieldName：   字段名称
        strFieldType：   字段类型
        nMinLen：        最小长度
        nMaxLen：        最大长度
        nCurLen：        当前长度
        strValueRange：  取值范围
        nNeedToCleared： 是否需要清洗
    返回值：
        True：更新成功， False：更新失败
    '''
    def UpdateProtocolMsgFieldInfo(self,model):
        bRetValue = False

        try:
            sqlCmdTxt = '''UPDATE BSC_BasicProtocolFieldInfo SET FieldName = '{}', FieldType = '{}',FieldIndex={}, StartPos = {}, FieldLen = {}, ValueRange = '{}', ToBeCleared={},IsFixed = {},IsRepeat = {},IsUpload = {} WHERE ProtocolID={} AND MsgID={} AND FieldID = {} '''.format(model.FieldName,model.FieldType,model.FieldIndex,model.StartPos,model.FieldLen,model.ValueRange, model.ToBeCleared,model.IsFixed,model.IsRepeat,model.IsUpload,model.ProtocolID,model.MsgID,model.FieldID)
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmdTxt)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            bRetValue = False
            self.Logger.error("Update protocol message field info with EXCEPTION:{}".format(e))
        finally:
            conn.close()

        return bRetValue


    # 删除报文信息中的字段信息
    '''
    参数：
        nProtocolID：报文ID
        nMsgID：     消息ID
        nFieldID：   字段ID
    返回值：
        True：删除成功， False：删除失败
    '''
    def RemoveProtocolMsgFieldInfo(self,nProtocolID,nMsgID,nFieldID):
        bRetValue = False
        try:
            sqlCmdTxt = "DELETE FROM BSC_BasicProtocolFieldInfo WHERE ProtocolID = {} AND MsgID = {} AND FieldID = {}".format(nProtocolID,nMsgID,nFieldID)
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmdTxt)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            bRetValue = False
            self.Logger.error("Remove protocol:{} message:{} field:{} info with EXCEPTION:{}".format(nProtocolID,nMsgID,nFieldID,e))
        return bRetValue


    def GetProtocolMsgFieldInfo(self):
        sqlCmdTxt= '''SELECT ProtocolID,MsgID,FieldID,FieldName,FieldType,FieldIndex,StartPos,FieldLen,ValueRange,ToBeCleared,IsFixed,IsRepeat,IsUpload FROM BSC_BasicProtocolFieldInfo'''
        lstProtocolMsgField = []
        try:
            conn = sqlite3.connect(self.DbFileName)
            result = conn.execute(sqlCmdTxt).fetchall()

            for r in result:
                model = ProtocolMsgFieldInfo()
                model.InitProtocolMsgFieldInfo(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11],r[12])
                lstProtocolMsgField.append(model)
        except BaseException as e:
            print('GetProtocolMsgFieldInfo with exception')
        finally:
            conn.close()

        return lstProtocolMsgField

    def GetChemCode(self):
        sqlCmdTxt = '''SELECT InstrumentName, ChemCode,TestItemCode FROM BSC_ChemCode'''
        lstChemCode = []

        try:
            conn = sqlite3.connect(self.DbFileName)
            result = conn.execute(sqlCmdTxt).fetchall()

            for c in result:
                model = ChemCodeInfo();
                model.InitializeInfo(c[0],c[1],c[2])
                lstChemCode.append(model)
        except BaseException as e:
            self.PublicMethods.Log("")
        finally:
            conn.close()

        return lstChemCode

    def GetModifiedChemCode(self):
        sqlCmdTxt = '''SELECT InstrumentName, ChemCode,TestItemCode FROM BSC_ChemCode WHERE IsModified = 1'''
        lstChemCode = []

        try:
            conn = sqlite3.connect(self.DbFileName)
            result = conn.execute(sqlCmdTxt).fetchall()

            for c in result:
                model = ChemCodeInfo();
                model.InitializeInfo(c[0], c[1], c[2])
                lstChemCode.append(model)
        except BaseException as e:
            self.PublicMethods.Log("")
        finally:
            conn.close()

        return lstChemCode

    def UpdateChemCode(self,model):
        sqlCmdTxt = '''UPDATE BSC_ChemCode SET TestItemCode = '{}' WHERE ChemCode = '{}' AND InstrumentName = '{}' '''.format(model.InstrumentName, model.TestItemCode,model.ChemCode)
        bRetValue = False
        try:
            conn = sqlite3.connect()
            conn.execute(sqlCmdTxt)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            self.PublicMethods.Log('')
        finally:
            conn.close()
        return bRetValue

    def InsertChemCode(self,data):
        sqlCmdTxt = '''INSERT INTO BSC_ChemCode(ChemCode,TestItemCode)VALUES (?,?)'''
        bRetValue = False
        try:
            conn = sqlite3.connect(self.DbFileName)
            cursor = conn.cursor()
            cursor.execute(sqlCmdTxt,data)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            print(e)
        finally:
            conn.close()

        return bRetValue

    def GetQCSampleInfo(self):

        lstQCSample = []

        try:
            sqlCmdTxt = "SELECT QCSampleNo,QCSampleType,InstrumentNo FROM BSC_QCSampleInfo"
            conn = sqlite3.connect(self.DbFileName)
            result = conn.execute(sqlCmdTxt).fetchall()

            for qcSample in result:
                model = QCSamlpeSetupInfo()
                model.InitQCSampleInfo(qcSample[0],qcSample[1],qcSample[2])
                lstQCSample.append(model)
        except BaseException as e:
            print('GetQCSampleInfo with exception')
        finally:
            conn.close()
        return lstQCSample

    def SaveQCSampleInfo(self,model):
        bRetValue = False

        try:
            sqlCmdTxt = '''INSERT INTo BSC_QCSampleInfo(QCSampleNo,QCSampleType,InstrumentNo)VALUES('{}','{}',{})'''.format(model.QCSampleNo,model.QCSampleType,model.InstrumentNo)
            print(sqlCmdTxt)
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmdTxt)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            print("SaveQCSampleInfo with exception")
        finally:
            conn.close()
        return bRetValue


    def DeleteQCSampleInfo(self,model):
        bRetValue = False

        try:
            sqlCmdTxt = '''DELETE FROM BSC_QCSampleInfo WHERE QCSampleNo = {} and InstrumentNo = {}'''.format(model.QCSampleNo,model.InstrumentNo)
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(sqlCmdTxt)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            print("DeleteQCSampleInfo with exception")
        finally:
            conn.close()
        return bRetValue

    def ExecuteSqlCmd(self,strSqlCmdTxt):
        bRetValue = False

        try:
            conn = sqlite3.connect(self.DbFileName)
            conn.execute(strSqlCmdTxt)
            conn.commit()
            bRetValue = True
        except BaseException as e:
            print('Error')
        finally:
            conn.close()

        return bRetValue

    