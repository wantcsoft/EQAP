

class ChemCodeInfo:
    def __init__(self):
        self.InstrumentName = ""
        self.ChemCode = ""
        self.TestItemCode = ""

    def InitializeInfo(self,strInstrumentName,strChemCode,strTestItemCode):
        self.InstrumentName = strInstrumentName
        self.ChemCode = strChemCode
        self.TestItemCode =strTestItemCode
