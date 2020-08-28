
class CommDataModel:
    def __init__(self):
        self.SerialNo = 0
        self.CommData = b''
        self.IsUploaded = 0
        self.ProtocolID = 0
        self.InstrumentName = ""
        self.RetryTimes = 0

    def InitializeInfo(self, nSerialNo, strData, nIsUploaded, nProtocolID, strInstrName, nRetryTimes, strCreateTime):
        self.SerialNo = nSerialNo
        self.CommData = bytes(strData)
        self.IsUploaded = nIsUploaded
        self.ProtocolID = nProtocolID
        self.InstrumentName =strInstrName
        self.RetryTimes = nRetryTimes
        self.CreateTime = strCreateTime

    def UpdateUploadFlag(self, nIsUploaded):
        self.IsUploaded = nIsUploaded
