import sqlite3

from Models.DeviceInfoModel import DeviceInfoModel
from Models.ProtocolFieldInfo import ProtocolFieldInfo
from Models.ProtocolInfo import ProtocolInfo
from Models.ProtocolMsgInfo import ProtocolMsgInfo
from Models.SysConfigInfo import SysConfigInfo
from Models.InstrumentInfo import InstrumentInfo


class PublicMethods:
    def __init__(self, strDBFilePath):
        self.DBFileName = strDBFilePath

    def GetSystemConfig(self):
        sql = '''SELECT SaveLog, TerminalID, TimeSequence, RetryTimes, DataKeptDays, LastDataCleanDate 
        FROM BSC_SysConfig'''
        conn = sqlite3.connect(self.DBFileName)
        result = conn.execute(sql).fetchone()
        if result is None:
            print('None')
            return SysConfigInfo(0, 0, 0, 0, 7, '2000-01-01')
        else:
            return SysConfigInfo(result[0], result[1], result[2], result[3], result[4], result[5])

    def UpdateSysConfig(self, nSaveLog, nTerminalID, nTimeSequence, nRetryTims, nDataKeptDays, dtLastCleanDate):
        sql = '''UPDATE BSC_SysConfig SET SaveLog = {}, TerminalID = {}, TimeSequence = {}, RetryTims = {}, 
        DataKeptDays={},LastDataCleanDate='{}' '''.format(nSaveLog, nTerminalID, nTimeSequence, nRetryTims,
                                                          nDataKeptDays, dtLastCleanDate)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql)
        conn.commit()
        conn.close()

    def GetDeviceInfoFromDB(self):
        device = DeviceInfoModel()
        sql = '''SELECT DeviceID, DeviceName, DeviceSerialNo, DeviceDesc, DeviceLocation, ServerIP, ServerPort, 
        TimeOut FROM BSC_DeviceInfo'''
        conn = sqlite3.connect(self.DBFileName)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is not None:
                device.InitDeviceInfo(result[0], result[1], result[2], result[3], result[4], result[5], result[6],
                                      result[7])
        except BaseException as e:
            print("Get communication data from DB with EXCEPTION:".format(e))
        finally:
            cursor.close()
            conn.close()

        return device

    def UpdateDeviceInfoToDB(self, nDeviceID, strDeviceName, strDeviceSerialNo, strDeviceDesc, strDeviceLocation,
                             strServerIP, nServerPort, fTimeout):
        bRetValue = False
        sql = '''UPDATE BSC_DeviceInfo SET DeviceName = '{}', DeviceSerialNo = '{}', DeviceDesc = '{}', 
        DeviceLocation = '{}',ServerIP = '{}',ServerPort = {},TimeOut = '{}' WHERE DeviceID = {} '''.format(
            strDeviceName, strDeviceSerialNo, strDeviceDesc, strDeviceLocation,
            strServerIP, nServerPort, fTimeout, nDeviceID)
        conn = sqlite3.connect(self.DBFileName)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            bRetValue = True
        except BaseException as e:
            # self.Logger.error("Get communication data from DB with EXCEPTION:".format(e))
            print(e)
        finally:
            cursor.close()
            conn.commit()
            conn.close()
        return bRetValue

    def GetProtocolList(self):
        sql = '''SELECT ProtocolID,ProtocolName,ProtocolType,IsEnabled FROM BSC_ProtocolInfo'''
        listProtocolModel = []
        conn = sqlite3.connect(self.DBFileName)
        try:
            listProtocol = conn.execute(sql).fetchall()
            for prot in listProtocol:
                protocol = ProtocolInfo()
                protocol.InitProtocolInfo(prot[0], prot[1], prot[2], prot[3])
                listProtocolModel.append(protocol.toJson())
        except BaseException as e:
            print("Get Protocol list from DB with EXCEPTION:".format(e))
        finally:
            conn.close()
        return listProtocolModel

    def UpdateProtocolInfo(self, ProtocolID, ProtocolName, ProtocolType, IsEnabled):
        sql = '''UPDATE BSC_ProtocolInfo SET ProtocolName = '{}', ProtocolType = '{}', IsEnabled = '{}' 
        where ProtocolID = {}'''.format(ProtocolName, ProtocolType, IsEnabled, ProtocolID)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql)
        conn.commit()
        conn.close()

    def SaveProtocolInfo(self, ProtocolName, ProtocolType, IsEnabled):
        sql = '''INSERT INTO BSC_ProtocolInfo(ProtocolName,ProtocolType,IsEnabled)VALUES('{}','{}',{})'''.format(
            ProtocolName, ProtocolType, IsEnabled)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql)
        conn.commit()

    def DeleteProtocolInfo(self, ProtocolID):
        sql1 = '''DELETE FROM BSC_ProtocolInfo WHERE ProtocolID = {}'''.format(ProtocolID)
        sql2 = '''DELETE FROM BSC_ProtocolMsgInfo WHERE ProtocolID = {}'''.format(ProtocolID)
        sql3 = '''DELETE FROM BSC_BasicProtocolFieldInfo WHERE ProtocolID = {}'''.format(ProtocolID)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql1)
        conn.execute(sql2)
        conn.execute(sql3)
        conn.commit()

    def GetMessageList(self, ProtocolID):
        sql = '''SELECT MsgID, ProtocolID, ProtocolMsgType, MsgHeader, MsgEndFlag, FieldCount, UploadFormat, 
        ToBeUpload, SampleIDFrom FROM BSC_ProtocolMsgInfo where ProtocolID = {}'''.format(ProtocolID)
        lstProtocolMsg = []
        conn = sqlite3.connect(self.DBFileName)
        try:
            lstProtocol = conn.execute(sql).fetchall()
            for prot in lstProtocol:
                protocolMsg = ProtocolMsgInfo(prot[0], prot[1], prot[2], prot[3], prot[4], prot[5], prot[6], prot[7],
                                              prot[8])
                lstProtocolMsg.append(protocolMsg.toJson())
        except BaseException as e:
            print("Get ProtocolMessage list from DB with EXCEPTION:".format(e))
        finally:
            conn.close()
        return lstProtocolMsg

    def UpdateMessageInfo(self, ProtocolMsgType, MsgHeader, MsgEndFlag, FieldCount, UploadFormat, ToBeUpload,
                          SampleIDFrom, ProtocolID, MsgID):
        sql = '''UPDATE BSC_ProtocolMsgInfo SET ProtocolMsgType={}, MsgHeader='{}', MsgEndFlag='{}', FieldCount={}, 
        UploadFormat='{}',ToBeUpload={}, SampleIDFrom='{}' where ProtocolID = {} AND MsgID={}'''.format(
            ProtocolMsgType, MsgHeader, MsgEndFlag, FieldCount, UploadFormat, ToBeUpload,
            SampleIDFrom, ProtocolID, MsgID)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql)
        conn.commit()
        conn.close()

    def SaveMessageInfo(self, ProtocolMsgType, MsgHeader, MsgEndFlag, FieldCount, UploadFormat,
                        ToBeUpload, SampleIDFrom, ProtocolID):
        sql = '''INSERT INTO BSC_ProtocolMsgInfo
                    (ProtocolMsgType, MsgHeader, MsgEndFlag, FieldCount, UploadFormat, ToBeUpload,
                    SampleIDFrom, ProtocolID)
                    VALUES({},'{}','{}',{},'{}',{},'{}',{})'''.format(ProtocolMsgType, MsgHeader, MsgEndFlag,
                                                                      FieldCount, UploadFormat, ToBeUpload,
                                                                      SampleIDFrom,
                                                                      ProtocolID)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql)
        conn.commit()

    def DeleteMessageInfo(self, MsgID):
        sql1 = '''DELETE FROM BSC_ProtocolMsgInfo WHERE MsgID = {}'''.format(MsgID)
        sql2 = '''DELETE FROM BSC_BasicProtocolFieldInfo WHERE MsgID = {}'''.format(MsgID)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql1)
        conn.execute(sql2)
        conn.commit()

    def GetFieldList(self, ProtocolID, MsgID):
        sql = '''SELECT FieldID, ProtocolID, MsgID, FieldName, FieldType, FieldIndex, 
                 StartPos,FieldLen, ValueRange, ToBeCleared, IsRepeat, IsUpload 
                 FROM BSC_BasicProtocolFieldInfo 
                 where ProtocolID = {} AND MsgID = {}'''.format(ProtocolID, MsgID)
        lstProtocolField = []
        conn = sqlite3.connect(self.DBFileName)
        try:
            lstProtocol = conn.execute(sql).fetchall()
            for prot in lstProtocol:
                protocolField = ProtocolFieldInfo(prot[0], prot[1], prot[2], prot[3], prot[4], prot[5], prot[6],
                                                  prot[7], prot[8], prot[9], prot[10], prot[11])
                lstProtocolField.append(protocolField.tojson())
        except BaseException as e:
            print("Get ProtocolField list from DB with EXCEPTION:".format(e))
        finally:
            conn.close()
        return lstProtocolField

    def UpdateFieldInfo(self, FieldName, FieldType, FieldIndex, StartPos, FieldLen, ValueRange, ToBeCleared,
                        IsRepeat, IsUpload, ProtocolID, MsgID, FieldID):
        sql = '''UPDATE BSC_BasicProtocolFieldInfo
                SET FieldName='{}', FieldType='{}', FieldIndex={}, StartPos={},FieldLen={}, ValueRange='{}', 
                ToBeCleared={}, IsRepeat={}, IsUpload={}
                where ProtocolID = {} AND MsgID={} AND FieldID={}'''.format(FieldName, FieldType, FieldIndex,
                                                                            StartPos, FieldLen, ValueRange, ToBeCleared,
                                                                            IsRepeat, IsUpload, ProtocolID, MsgID,
                                                                            FieldID)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql)
        conn.commit()
        conn.close()

    def SaveFieldInfo(self, FieldName, FieldType, FieldIndex, StartPos, FieldLen, ValueRange, ToBeCleared,
                      IsRepeat, IsUpload, ProtocolID, MsgID):
        sql = '''INSERT INTO BSC_BasicProtocolFieldInfo
                        (FieldName, FieldType, FieldIndex, StartPos,FieldLen, ValueRange, 
                        ToBeCleared, IsRepeat, IsUpload,ProtocolID, MsgID)
                        VALUES ('{}','{}',{},{},{},'{}',{},{},{},{},{})'''.format(FieldName, FieldType, FieldIndex,
                                                                                  StartPos, FieldLen, ValueRange,
                                                                                  ToBeCleared, IsRepeat, IsUpload,
                                                                                  ProtocolID, MsgID)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql)
        conn.commit()

    def DeleteFieldInfo(self, FieldID):
        sql = '''DELETE FROM BSC_BasicProtocolFieldInfo WHERE FieldID = {}'''.format(FieldID)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql)
        conn.commit()

    def GetInstrumentInfoFromDB(self):
        sql = '''SELECT BSC_InstrumentInfo.InstrumentNo, BSC_InstrumentInfo.InstrumentID, 
        BSC_InstrumentInfo.InstrumentName, BSC_InstrumentInfo.InstrumentSerialNo, 
        BSC_InstrumentInfo.InstrumentDesc, BSC_InstrumentInfo.InstrumentLocation, 
        BSC_InstrumentInfo.HighConcentrationID, BSC_InstrumentInfo.MidConcentrationID, 
        BSC_InstrumentInfo.LowConcentrationID, BSC_InstrumentInfo.ProtocolID, 
        BSC_InstrumentInfo.BaudRate, BSC_InstrumentInfo.PortName, BSC_InstrumentInfo.IsActive,
        BSC_ProtocolInfo.ProtocolName
        FROM BSC_InstrumentInfo, BSC_ProtocolInfo
        WHERE BSC_InstrumentInfo.ProtocolID = BSC_ProtocolInfo.ProtocolID'''
        conn = sqlite3.connect(self.DBFileName)
        listInstrumentModel = []
        cursor = conn.cursor()
        try:
            listInstrument = conn.execute(sql).fetchall()
            for prot in listInstrument:
                instrument = InstrumentInfo()
                instrument.InitInstrumentInfo(prot[0], prot[1], prot[2], prot[3], prot[4], prot[5],
                                              prot[6], prot[7], prot[8], prot[9], prot[10], prot[11],
                                              prot[12], prot[13])
                listInstrumentModel.append(instrument.toJson())

        except BaseException as e:
            print("Get communication data from DB with EXCEPTION:".format(e))
        finally:
            cursor.close()
            conn.close()

        return listInstrumentModel

    def UpdateInstrumentInfoToDB(self, InstrumentNo, InstrumentID, InstrumentName, InstrumentSerialNo, InstrumentDesc,
                                 InstrumentLocation, HighConcentrationID, MidConcentrationID, LowConcentrationID,
                                 ProtocolID, BaudRate, PortName, IsActive):
        bRetValue = False
        sql = '''UPDATE BSC_InstrumentInfo SET InstrumentID = '{}', InstrumentName = '{}', InstrumentSerialNo = '{}', 
        InstrumentDesc = '{}', InstrumentLocation = '{}',HighConcentrationID = '{}',MidConcentrationID = '{}', 
        LowConcentrationID = '{}', ProtocolID = {}, BaudRate = {}, PortName = '{}', IsActive = {} 
        WHERE InstrumentNo = {} '''.format(InstrumentID, InstrumentName, InstrumentSerialNo, InstrumentDesc,
                                           InstrumentLocation, HighConcentrationID, MidConcentrationID,
                                           LowConcentrationID, ProtocolID, BaudRate, PortName, IsActive,
                                           InstrumentNo)
        conn = sqlite3.connect(self.DBFileName)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            bRetValue = True
        except BaseException as e:
            # self.Logger.error("Get communication data from DB with EXCEPTION:".format(e))
            print("Get communication data from DB with EXCEPTION:".format(e))
        finally:
            cursor.close()
            conn.commit()
            conn.close()
        return bRetValue

    def SaveInstrumentInfo(self, InstrumentID, InstrumentName, InstrumentSerialNo, InstrumentDesc,
                           InstrumentLocation, HighConcentrationID, MidConcentrationID, LowConcentrationID,
                           ProtocolID, BaudRate, PortName, IsActive):
        sql = '''INSERT INTO BSC_InstrumentInfo(InstrumentID, InstrumentName, InstrumentSerialNo, InstrumentDesc,
                                 InstrumentLocation, HighConcentrationID, MidConcentrationID, LowConcentrationID,
                                 ProtocolID, BaudRate, PortName, IsActive)VALUES('{}', '{}', '{}', '{}', '{}', 
                                 '{}', '{}', '{}', {}, {}, '{}', {})'''.format(
            InstrumentID, InstrumentName, InstrumentSerialNo, InstrumentDesc, InstrumentLocation,
            HighConcentrationID, MidConcentrationID, LowConcentrationID, ProtocolID, BaudRate, PortName, IsActive)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql)
        conn.commit()

    def DeleteInstrumentInfo(self, InstrumentNo):
        sql = '''DELETE FROM BSC_InstrumentInfo WHERE InstrumentNo = {}'''.format(InstrumentNo)
        conn = sqlite3.connect(self.DBFileName)
        conn.execute(sql)
        conn.commit()
