

class QCSamlpeSetupInfo:
    def __init__(self):
        self.QCSampleNo = ""
        self.QCSampleType = ""
        self.InstrumentNo = 0

    def InitQCSampleInfo(self,strQCSampleNo,strQCSampleType,nInstrumentNo):
        self.QCSampleNo = strQCSampleNo
        self.QCSampleType = strQCSampleType
        self.InstrumentNo = nInstrumentNo