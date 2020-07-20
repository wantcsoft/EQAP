
from Models.QCSampleModel import QCSampleModel
from Models.QCResultModel import QCResultModel
class ProtocolMsgInfo:
    def __init__(self):
        self.ProtocolID = 0
        self.MsgID = 0
        self.MsgTypeID = 0
        self.MsgHeader = ""
        self.MsgEnd = ""
        self.FieldCount = 0
        self.UploadFormat = ''
        self.ToBeUpload = False
        self.Fields = []
        self.SampleIDFrom = ""

    def InitProtocolMsgInfo(self,nMsgID,nProtocolID,nMsgTypeID,strMsgHeader,strMsgEnd,nFieldCount,strUploadFormat,nToBeUpload,strSampleIDFrom):
        self.ProtocolID = nProtocolID
        self.MsgID = nMsgID
        self.MsgTypeID = nMsgTypeID
        self.MsgHeader = strMsgHeader
        self.MsgEnd = strMsgEnd
        self.FieldCount = nFieldCount
        self.UploadFormat = strUploadFormat
        self.ToBeUpload = nToBeUpload == 1
        self.SampleIDFrom = strSampleIDFrom
        self.FixLength = 0
        self.RepleatLength = 0
        return True

    def AddProtocolMsgField(self,model):
        bFound = False
        for f in self.Fields:
            if f.ProtocolID == model.ProtocolID and f.MsgID == model.MsgID and f.FieldID == model.FieldID:
                bFound = True
                break

        if model.IsFixed == 1:
            self.FixLength += model.FieldLen
        if model.IsRepeat == 1:
            self.RepleatLength += model.FieldLen
        if bFound == False:
            self.Fields.append(model)

        return True

    def ParseCommData(self,data,lstChemCode,lstQCSample):
        if len(data) < self.FixLength + self.RepleatLength:
            return None

        qcSample = QCSampleModel()

        qcSampleNo = ""
        qcSampleType = "\\"

        nFixDataLen = 0
        for mf in self.Fields:
            if mf.IsRepeat == 1:
                continue

            if mf.FieldName.upper() == "BlockIde".upper():
                nFixDataLen = mf.StartPos + mf.FieldLen
                continue

            fieldValue = "\\"
            if mf.FieldLen > 0 and mf.ToBeCleared == False:
                fieldValue = data[mf.StartPos:mf.StartPos + mf.FieldLen].strip()
                if len(fieldValue) == 0:
                    fieldValue = "\\"
            if mf.FieldName == "QC_Type":
                qcSampleType = fieldValue
            if mf.FieldName == "SampleNo":
                qcSampleNo = fieldValue
            qcSampleProperty = (mf.FieldName,fieldValue,mf.IsUpload)
            qcSample.Properties.append(qcSampleProperty)

        if qcSampleType == "\\" :
            for qc in lstQCSample:
                if qc.QCSampleNo == qcSampleNo:
                    qcSampleType = qc.QCSampleType
                    break

        sampleID = "\\"

        for sp in qcSample.Properties:
            if sp[0].upper() == self.SampleIDFrom.upper():
                sampleID = sp[1]
                break

        for index in range(len(qcSample.Properties)):
            if qcSample.Properties[index][0] == "SampleID":
                prop = (qcSample.Properties[index][0],sampleID,qcSample.Properties[index][2])
                qcSample.Properties[index] = prop
                break

            if qcSample.Properties[index][0] == "QC_Type" and qcSample.Properties[index][1] == "\\":
                prop = (qcSample.Properties[index][0],qcSampleType,qcSample.Properties[index][2])
                qcSample.Properties[index] = prop
        
        strRepeat = data[nFixDataLen:len(data)]

        while len(strRepeat) > 0:
            nRepeatLen = 0
            qcResult = QCResultModel()
            bTestItemFound = False
            for mf in self.Fields:
                if mf.IsRepeat == 0:
                    continue

                nRepeatLen += mf.FieldLen
                fieldValue = "\\"

                if mf.FieldLen > 0 and mf.ToBeCleared == False:
                    fieldValue = strRepeat[mf.StartPos:mf.StartPos + mf.FieldLen].strip()

                resultData = (mf.FieldName,fieldValue,mf.IsUpload)
                qcResult.Properties.append(resultData)

                testItem = ""
                if mf.FieldName.upper() == "ChemID".upper():
                    for cc in lstChemCode:
                        if cc.ChemCode == fieldValue:
                            testItem = cc.TestItemCode
                            bTestItemFound = True
                            break

                    resultData = ("TestItem",testItem,1)
                    qcResult.Properties.append(resultData)

            if bTestItemFound == True:
                qcSample.AddResult(qcResult)
            strRepeat = strRepeat[nRepeatLen:len(strRepeat)]

        return qcSample