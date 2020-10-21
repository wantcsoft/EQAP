class InstrumentInfo:
    def __init__(self):
        self.InstrumentNo = 0
        self.InstrumentID = 0
        self.InstrumentName = ''
        self.InstrumentSerialNo = 0
        self.InstrumentDesc = ''
        self.InstrumentLocation = ''
        self.HighConcentrationID = ''
        self.MidConcentrationID = ''
        self.LowConcentrationID = ''
        self.ProtocolID = 0
        self.BaudRate = 0
        self.PortName = ''
        self.IsActive = False

        self.ProtocolName = ''

    def InitInstrumentInfo(self, InstrumentNo, InstrumentID, InstrumentName, InstrumentSerialNo, InstrumentDesc,
                           InstrumentLocation, HighConcentrationID, MidConcentrationID, LowConcentrationID,
                           ProtocolID, BaudRate, PortName, IsActive, ProtocolName):
        self.InstrumentNo = InstrumentNo
        self.InstrumentID = InstrumentID
        self.InstrumentName = InstrumentName
        self.InstrumentSerialNo = InstrumentSerialNo
        self.InstrumentDesc = InstrumentDesc
        self.InstrumentLocation = InstrumentLocation
        self.HighConcentrationID = HighConcentrationID
        self.MidConcentrationID = MidConcentrationID
        self.LowConcentrationID = LowConcentrationID
        self.ProtocolID = ProtocolID
        self.BaudRate = BaudRate
        self.PortName = PortName
        self.IsActive = IsActive == 1
        self.ProtocolName = ProtocolName

    def toJson(self):
        proJson = {}
        proJson["InstrumentNo"] = self.InstrumentNo
        proJson["InstrumentID"] = self.InstrumentID
        proJson["InstrumentName"] = self.InstrumentName
        proJson["InstrumentSerialNo"] = self.InstrumentSerialNo
        proJson["InstrumentDesc"] = self.InstrumentDesc
        proJson["InstrumentLocation"] = self.InstrumentLocation
        proJson["HighConcentrationID"] = self.HighConcentrationID
        proJson["MidConcentrationID"] = self.MidConcentrationID
        proJson["LowConcentrationID"] = self.LowConcentrationID
        proJson["ProtocolID"] = self.ProtocolID
        proJson["BaudRate"] = self.BaudRate
        proJson["PortName"] = self.PortName
        proJson["IsActive"] = self.IsActive

        proJson["ProtocolName"] = self.ProtocolName
        return proJson
