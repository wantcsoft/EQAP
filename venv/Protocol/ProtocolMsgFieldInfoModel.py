

class ProtocolMsgFieldInfo:
    def __init__(self):
        self.ProtocolID = 0
        self.MsgID = 0
        self.FieldID = 0
        self.FieldName = ''
        self.FieldType = ''
        self.FieldIndex = 0
        self.StartPos = 0
        self.FieldLen = 0
        self.ValueRange = ''
        self.ToBeCleared = False
        self.IsFixed = 0
        self.IsRepeat = 0
        self.IsUpload  =0
        return

    def InitProtocolMsgFieldInfo(self,nProtocolID,nMsgID,nFieldID,strFieldName,strFieldType,nFieldIndex,nStartPos,nFieldLen,strValueRange,nToBeCleared,nIsFixed,nIsRepeat,nIsUpload):
        self.ProtocolID = nProtocolID
        self.MsgID = nMsgID
        self.FieldID = nFieldID
        self.FieldName = strFieldName
        self.FieldType = strFieldType
        self.FieldIndex = nFieldIndex
        self.StartPos = nStartPos
        self.FieldLen = nFieldLen
        self.ValueRange = strValueRange
        self.ToBeCleared = nToBeCleared == 1
        self.IsFixed = nIsFixed
        self.IsRepeat = nIsRepeat
        self.IsUpload = nIsUpload
        return