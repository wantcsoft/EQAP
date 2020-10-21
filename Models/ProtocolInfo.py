
class ProtocolInfo:
    def __init__(self):
        self.ProtocolID = 0
        self.ProtocolName = ''
        self.ProtocolType = ''
        self.IsEnabled = False

    def InitProtocolInfo(self,nProtocolID,strProtocolName,strProtocolType,nIsEnabled):
        self.ProtocolID = nProtocolID
        self.ProtocolName = strProtocolName
        self.ProtocolType = strProtocolType
        self.IsEnabled = nIsEnabled == 1

    def toJson(self):
        proJson = {}
        proJson["ProtocolID"] = self.ProtocolID
        proJson["ProtocolName"] = self.ProtocolName
        proJson["ProtocolType"] = self.ProtocolType
        proJson["IsEnabled"] = self.IsEnabled
        return proJson
