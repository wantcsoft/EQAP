from Protocol.ProtocolMsgInfoModel import ProtocolMsgInfo


class ProtocolInfo:
    def __init__(self):
        self.ProtocolID = 0
        self.ProtocolName = ''
        self.ProtocolType = ''
        self.IsEnabled = False
        self.ProtocolMsg = []

    def InitProtocolInfo(self,nProtocolID,strProtocolName,strProtocolType,nIsEnabled):
        self.ProtocolID = nProtocolID
        self.ProtocolName = strProtocolName
        self.ProtocolType = strProtocolType
        self.IsEnabled = nIsEnabled == 1

    def AddProtocolMsgItem(self,protocolMsgItem):
        bFound = False
        for p in self.ProtocolMsg:
            if p.ProtocolID == protocolMsgItem.ProtocolID and p.MsgID == protocolMsgItem.MsgID:
                continue
        if bFound == False:
            self.ProtocolMsg.append(protocolMsgItem)

    # 参数 data 的类型为 CommDataModel
    def ParseData(self,data,lstChemCode,lstQCSample):
        if data is None:
            return []

        instrName = data.InstrumentName
        commData = str(data.CommData,encoding='utf-8')

        dataHeader = commData[0:2].strip()

        msgFlag = ""
        qcSample = None
        for pm in self.ProtocolMsg:
            if pm.MsgHeader == dataHeader:
                qcSample = pm.ParseCommData(commData,instrName,lstChemCode,lstQCSample)
                msgFlag = pm.UploadFormat
                break;

        if qcSample is None:
            return []


        return qcSample.FormatForUpload(data.InstrumentName,msgFlag,data.CreateTime)
