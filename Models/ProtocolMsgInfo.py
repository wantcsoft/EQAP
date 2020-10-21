
class ProtocolMsgInfo:
    def __init__(self,MsgID,ProtocolID,ProtocolMsgType,MsgHeader,MsgEndFlag,
                 FieldCount,UploadFormat,ToBeUpload,SampleIDFrom):
        self.MsgID = MsgID
        self.ProtocolID = ProtocolID
        self.ProtocolMsgType = ProtocolMsgType
        self.MsgHeader = MsgHeader
        self.MsgEndFlag = MsgEndFlag
        self.FieldCount = FieldCount
        self.UploadFormat = UploadFormat
        self.ToBeUpload = ToBeUpload
        self.SampleIDFrom = SampleIDFrom


    def toJson(self):
        devJson = {}
        devJson["MsgID"] = self.MsgID
        devJson["ProtocolID"] = self.ProtocolID
        devJson["ProtocolMsgType"] = self.ProtocolMsgType
        devJson["MsgHeader"] = self.MsgHeader
        devJson["MsgEndFlag"] = self.MsgEndFlag
        devJson["FieldCount"] = self.FieldCount
        devJson["UploadFormat"] = self.UploadFormat
        devJson["ToBeUpload"] = self.ToBeUpload
        devJson["SampleIDFrom"] = self.SampleIDFrom
        return devJson
