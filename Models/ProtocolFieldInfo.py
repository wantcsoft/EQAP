class ProtocolFieldInfo:
    def __init__(self,FieldID, ProtocolID, MsgID, FieldName, FieldType, FieldIndex, StartPos,
                 FieldLen, ValueRange, ToBeCleared, IsRepeat, IsUpload):
        self.FieldID = FieldID
        self.ProtocolID = ProtocolID
        self.MsgID = MsgID
        self.FieldName = FieldName
        self.FieldType = FieldType
        self.FieldIndex = FieldIndex
        self.StartPos = StartPos
        self.FieldLen = FieldLen
        self.ValueRange = ValueRange
        self.ToBeCleared = ToBeCleared
        self.IsRepeat = IsRepeat
        self.IsUpload = IsUpload

    def tojson(self):
        fieldJson = {}
        fieldJson["FieldID"] = self.FieldID
        fieldJson["ProtocolID"] = self.ProtocolID
        fieldJson["MsgID"] = self.MsgID
        fieldJson["FieldName"] = self.FieldName
        fieldJson["FieldType"] = self.FieldType
        fieldJson["FieldIndex"] = self.FieldIndex
        fieldJson["StartPos"] = self.StartPos
        fieldJson["FieldLen"] = self.FieldLen
        fieldJson["ValueRange"] = self.ValueRange
        fieldJson["ToBeCleared"] = self.ToBeCleared
        fieldJson["IsRepeat"] = self.IsRepeat
        fieldJson["IsUpload"] = self.IsUpload
        return fieldJson
