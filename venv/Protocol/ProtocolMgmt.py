from Protocol.ProtocolInfo import ProtocolInfo
from Protocol.ProtocolMsgInfoModel import ProtocolMsgInfo
from Protocol.ProtocolMsgFieldInfoModel import ProtocolMsgFieldInfo
import time

class ProtocolMgmt:
    def __init__(self):
        self.ProtocolList = []
        self.ChemCodeList = []
        self.QCSampleList = []

    def SetProtocolList(self,lstProtocol):
        if len(lstProtocol) == 0:
            return False
        self.ProtocolList.clear()
        for p in lstProtocol:
            self.ProtocolList.append(p)
        return True

    def SetProtocolMsgList(self,lstProtocolMsg):
        if len(lstProtocolMsg) == 0:
            return False

        for p in self.ProtocolList:
            for pm in lstProtocolMsg:
                if p.ProtocolID == pm.ProtocolID:
                    p.AddProtocolMsgItem(pm)

        return True

    def SetProtocolMsgFieldList(self,lstProtocolMsgField):
        if len(lstProtocolMsgField) == 0:
            return False

        for p in self.ProtocolList:
            for pm in p.ProtocolMsg:
                for pmf in lstProtocolMsgField:
                    if pmf.ProtocolID == pm.ProtocolID and pmf.MsgID == pm.MsgID:
                        pm.AddProtocolMsgField(pmf)

        return True

    def SetChemCodeList(self,lstChemCode):
        if len(lstChemCode) == 0:
            return False

        for c in lstChemCode:
            self.ChemCodeList.append(c)

    def SetQCSampleList(self,lstQCSample):
        for q in lstQCSample:
            self.QCSampleList.append(q)

    def CheckMsgIsDefined(self,data,nProtocolID):
        nDataLen  =len(data)
        if nDataLen == 0:
            return False

        for p in self.ProtocolList:
            if p.ProtocolID != nProtocolID:
                continue

            for pMsg in p.ProtocolMsg:
                if pMsg.MsgHeader == str(data[0:2],encoding='utf-8').strip():
                    return True
        return False

    def ParseCommData(self,data):
        protocol = None
        for p in self.ProtocolList:
            if p.ProtocolID == data.ProtocolID:
                return p.ParseData(data,self.ChemCodeList,self.QCSampleList)

        return []

        # lstRet = []
        # # 判断传入的数据是否为空
        # if data is None:
        #     return lstRet
        #
        # # 根据串口设定的报文ID，获得对应的报文设置
        # protocol = None
        # for p in self.ProtocolList:
        #     if p.ProtocolID == data.ProtocolID:
        #         protocol = p
        #         break;
        # print("Communication Data:",data.CommData)
        # # 如果为配置对应的报文，则返回原始数据
        # if protocol is None:
        #     lstRet.append(data.CommData)
        #     return data
        #
        # nFixDataLen = 0
        # # 去除报文的开始和结束标记
        # dataToParse = data.CommData
        #
        # # 获得报文信息的标记
        # flagInData = dataToParse[0:2]
        # protocolMsg = None
        #
        # # 循环报文设置中的消息设置，根据数据的标记提取对应的消息设置
        # for m in protocol.ProtocolMsg:
        #     msgHeader = m.MsgHeader;
        #
        #     if len(msgHeader) == 1:
        #         msgHeader += " "
        #     if flagInData == bytes(msgHeader,encoding='utf-8'):
        #         protocolMsg = m;
        #         break
        #
        # # 如果不存在对应的报文标记设置，则返回原始数据
        # if protocolMsg is None:
        #     lstRet.append(data.CommData)
        #     return lstRet
        #
        # # 获得消息上传的格式
        # dataFormat = protocolMsg.UploadFormat;
        # instrName = data.InstrumentName
        # timeStr = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        #
        # sysNo = "\\"
        # rackNo = "\\"
        # cupNo = "\\"
        # sampleType = "\\"
        # sampleNo = "\\"
        # sampleID = "\\"
        # dummy = "\\"
        # sex = "\\"
        # years = "\\"
        # months = "\\"
        # pid1 = "\\"
        # pid2 = "\\"
        # pid3 = "\\"
        # pid4 = "\\"
        # pid5 = "\\"
        # pid6 = "\\"
        # blockIde = "E"
        #
        # uploadString = "InstrumentList\t" + instrName
        # uploadField = "TableData\tInstrumentID\tTimeID\tQC_SN\tQC_ValidDate\tTestTime"
        # uploadFieldType = "\tSN\tSN\tSN\tSN\tSN"
        # uploadFixValue = "\t" + instrName + "\t" + timeStr + "\t\\\t\\\t" + timeStr
        #
        # nReportStartPos = 0
        # for fs in protocolMsg.Fields:
        #     if fs.FieldLen == 0:
        #         continue
        #
        #     if fs.FieldName == "SampleID":
        #         sampleID = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         strSampleID = str(sampleID, encoding='utf-8')
        #         strSampleID = strSampleID.strip()
        #         if len(strSampleID) == 0:
        #             strSampleID = "\\"
        #
        #         if fs.IsUpload == 1:
        #             uploadField += "\tSampleID"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue+= "\t" + strSampleID
        #         print('SampleID:',strSampleID)
        #
        #     if fs.FieldName == "SampleNo":
        #         print('SampleNo field should be parse')
        #         sampleNo = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tSampleNo"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + str(sampleNo,encoding='utf-8')
        #         print("SampleNo:",sampleNo)
        #
        #     if fs.FieldName == "RackNo":
        #         rackNo = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tRackNo"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + str(rackNo,encoding='utf-8')
        #         print("RackNo:",rackNo)
        #     if fs.FieldName == "CupNo":
        #         cupNo = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tCupNo"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + cupNo
        #         print("CupNo:", cupNo)
        #     if fs.FieldName == "Dummy":
        #         dummy = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tDummy"
        #             uploadFieldType += "\tSN"
        #             strDummy = str(dummy, encoding='utf-8')
        #             strDummy = strDummy.strip()
        #             if len(strDummy) == 0:
        #                 strDummy = "\\"
        #             uploadFixValue += "\t" + strDummy
        #         print("Dummy:", strDummy)
        #     if fs.FieldName == "BlockIde":
        #         blockIde = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         nReportStartPos = fs.StartPos + fs.FieldLen
        #     if fs.FieldName == "Sex":
        #         sex = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tSex"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + sex
        #         print("Sex:", sex)
        #     if fs.FieldName == "Years":
        #         years = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tYears"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + years
        #         print("Years:", years)
        #     if fs.FieldName == "Months":
        #         months = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tMonths"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + months
        #             print("Months:", months)
        #     if fs.FieldName == "PID1":
        #         pid1 = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tPID1"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + pid1
        #         print("PID1:", pid1)
        #     if fs.FieldName == "PID2":
        #         pid2 = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tPID2"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + pid2
        #         print("PID2:", pid2)
        #     if fs.FieldName == "PID3":
        #         pid3 = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tPID3"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + pid3
        #         print("PID3:", pid3)
        #     if fs.FieldName == "PID4":
        #         pid4 = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tPID4"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + pid4
        #         print("PID4:", pid4)
        #     if fs.FieldName == "PID5":
        #         pid5 = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tPID5"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + pid5
        #         print("PID5:", pid5)
        #     if fs.FieldName == "PID6":
        #         pid6 = data.CommData[fs.StartPos:fs.StartPos + fs.FieldLen]
        #         if fs.IsUpload == 1:
        #             uploadField += "\tPID6"
        #             uploadFieldType += "\tSN"
        #             uploadFixValue += "\t" + pid6
        #         print("PID6:", pid6)
        #
        #
        #
        # unit = b"\\"
        # curvette = b"\\"
        # chemID = "\\"
        # testItemCode = "\\"
        # testTime = timeStr
        # result = "\\"
        # qcSn = "\\"
        # qcValidDate = "\\"
        # rgn1 = b"\\"
        # rgn2 = b"\\"
        # rgn3 = b"\\"
        # rgn4 = b"\\"
        # dataFlag = "\\"
        #
        # bytesRepeat = data.CommData[nReportStartPos:len(data.CommData)]
        # strRepeat = str(bytesRepeat,encoding='utf-8')
        # uploadValue = ""
        # bResultFieldToFromatString = False
        # while len(strRepeat) > 0:
        #     nRepeatDataLen = 0
        #     repeatValueString = uploadFixValue
        #     for fs in protocolMsg.Fields:
        #         if fs.IsRepeat == 0:
        #             continue
        #
        #         if fs.IsUpload == 0:
        #             continue
        #
        #         if fs.FieldName == "Unit":
        #             if fs.FieldLen > 0:
        #                 unit = bytesRepeat[fs.StartPos:fs.StartPos + fs.FieldLen]
        #             nRepeatDataLen += fs.FieldLen
        #             if bResultFieldToFromatString == False:
        #                 uploadField += "\t" + fs.FieldName
        #                 uploadFieldType += "\tSN"
        #                 repeatValueString += unit
        #
        #         if fs.FieldName == "Cuvette":
        #             if fs.FieldLen > 0:
        #                 curvette = bytesRepeat[fs.StartPos:fs.StartPos + fs.FieldLen]
        #             nRepeatDataLen += fs.FieldLen
        #             if bResultFieldToFromatString == False:
        #                 uploadField += "\t" + fs.FieldName
        #                 uploadFieldType += "\tSN"
        #                 repeatValueString += curvette
        #
        #         if fs.FieldName == "ChemID":
        #             chemID = bytesRepeat[fs.StartPos:fs.StartPos + fs.FieldLen]
        #             strChemID = str(chemID,encoding='utf-8')
        #             nRepeatDataLen += fs.FieldLen
        #             if bResultFieldToFromatString == False:
        #                 uploadField += "\t" + fs.FieldName
        #                 uploadFieldType += "\tSN"
        #                 repeatValueString += "\t" +strChemID
        #
        #                 for chem in self.ChemCodeList:
        #                     if chem.ChemCode == strChemID:
        #                         uploadField += "\tTestItem"
        #                         uploadFieldType += "\tSN"
        #                         repeatValueString += "\t" + chem.TestItemCode
        #
        #
        #         if fs.FieldName == "RG_SN1":
        #             if fs.FieldLen > 0:
        #                 rgn1 = bytesRepeat[fs.StartPos:fs.StartPos + fs.FieldLen]
        #
        #             nRepeatDataLen += fs.FieldLen
        #             if bResultFieldToFromatString == False:
        #                 uploadField += "\t" + fs.FieldName
        #                 uploadFieldType += "\tSN"
        #                 repeatValueString += "\t" + str(rgn1,encoding = 'utf-8')
        #
        #         if fs.FieldName == "RG_SN2":
        #             if fs.FieldLen > 0:
        #                 rgn2 = bytesRepeat[fs.StartPos:fs.StartPos + fs.FieldLen]
        #             nRepeatDataLen += fs.FieldLen
        #             if bResultFieldToFromatString == False:
        #                 uploadField += "\t" + fs.FieldName
        #                 uploadFieldType += "\tSN"
        #                 repeatValueString += "\t" + str(rgn2,encoding = 'utf-8')
        #
        #         if fs.FieldName == "RG_SN3":
        #             if fs.FieldLen > 0:
        #                 rgn3 = bytesRepeat[fs.StartPos:fs.StartPos + fs.FieldLen]
        #             nRepeatDataLen += fs.FieldLen
        #             if bResultFieldToFromatString == False:
        #                 uploadField += "\t" + fs.FieldName
        #                 uploadFieldType += "\tSN"
        #                 repeatValueString += "\t" + str(rgn3,encoding = 'utf-8')
        #
        #         if fs.FieldName == "RG_SN4":
        #             if fs.FieldLen > 0:
        #                 rgn4 = bytesRepeat[fs.StartPos:fs.StartPos + fs.FieldLen]
        #             nRepeatDataLen += fs.FieldLen
        #             print("RGN4",rgn4)
        #             if bResultFieldToFromatString == False:
        #                 uploadField += "\t" + fs.FieldName
        #                 uploadFieldType += "\tSN"
        #                 repeatValueString += "\t" + str(rgn4,encoding = 'utf-8')
        #
        #         if fs.FieldName == "TestValue":
        #             result = bytesRepeat[fs.StartPos:fs.StartPos + fs.FieldLen]
        #             nRepeatDataLen += fs.FieldLen
        #             if bResultFieldToFromatString == False:
        #                 uploadField += "\t" + fs.FieldName
        #                 uploadFieldType += "\tSN"
        #                 repeatValueString += "\t" + str(result,encoding = 'utf-8').strip()
        #
        #         if fs.FieldName == "DataFlags":
        #             dataFlag = bytesRepeat[fs.StartPos:fs.StartPos + fs.FieldLen]
        #             nRepeatDataLen += fs.FieldLen
        #             if bResultFieldToFromatString == False:
        #                 uploadField += "\t" + fs.FieldName
        #                 uploadFieldType += "\tSN"
        #                 repeatValueString += str(dataFlag,encoding = 'utf-8')
        #
        #     qcType = '\\'
        #     for q in self.QCSampleList:
        #         print('QCSampleNo',q.QCSampleNo,sampleNo)
        #         if q.QCSampleNo == str(sampleNo,encoding='utf-8'):
        #             qcType = q.QCSampleType
        #     print('QC_Type',qcType)
        #
        #     uploadField += "\tQC_Type"
        #     uploadFieldType += "\tSN"
        #     repeatValueString += "\t" + qcType
        #
        #     bResultFieldToFromatString = True
        #
        #     bytesRepeat = bytesRepeat[nRepeatDataLen:len(bytesRepeat)]
        #     strRepeat = str(bytesRepeat, encoding='utf-8').strip()
        #
        #     uploadString = uploadString + "\r" + uploadField + "\r" + uploadFieldType + "\r" + repeatValueString + "\rMessageID\t" + dataFormat
        #     lstRet.append(uploadString)
        #
        #     # print(type(uploadString),uploadString,len(uploadString))
        #     print(type(uploadField),uploadField)
        #     print(type(uploadFieldType),uploadFieldType)
        #     print(type(repeatValueString),repeatValueString)
        # return lstRet