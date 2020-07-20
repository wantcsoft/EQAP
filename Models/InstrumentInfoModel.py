
class InstrumentInfoModel:
    def __init__(self):
        self.InstrumentNo = 0
        self.InstrumentName = ''
        self.InstrumentSerialNo = ''
        self.InstrumentDesc = ''
        self.InstrumentLocation = ''
        self.HighConcentrationID = ''
        self.MidConcentrationID = ''
        self.LowConcentrationID = ''
        self.ProtocolID = ''
        self.BaudRate = ''
        self.PortName = ''
        self.IsActive = False

    def InitInstrumentInfo(self,nInstrNo,strInstrName,strInstrSerial,strInstrDesc,strInstrLocation,strHighConcentID,strMidConcentID,strLowConcentID,nProtocolID,nBaudRate,strPortName,nIsActive):
        self.InstrumentNo = nInstrNo
        self.InstrumentName = strInstrName
        self.InstrumentSerialNo = strInstrSerial
        self.InstrumentDesc = strInstrDesc
        self.InstrumentLocation = strInstrLocation
        self.HighConcentrationID = strHighConcentID
        self.MidConcentrationID = strMidConcentID
        self.LowConcentrationID = strLowConcentID
        self.ProtocolID = nProtocolID
        self.BaudRate = nBaudRate
        self.PortName = strPortName
        self.IsActive = nIsActive == 1

