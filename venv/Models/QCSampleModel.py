
'''
这个类是解析报文后所形成的对象，会包含多个测试结果
'''

import time

class QCSampleModel:
    def __init__(self):
        self.SysNo = "\\"
        self.RackNo = "\\"
        self.CupNo = "\\"
        self.SampleType = "\\"
        self.SampleNo = "\\"
        self.SampleID = "\\"
        self.Dummy = "\\"
        self.ControlNo = "\\"
        self.Sex = "\\"
        self.Years = "\\"
        self.Months = "\\"
        self.Pid1 = "\\"
        self.Pid2 = "\\"
        self.Pid3 = "\\"
        self.Pid4 = "\\"
        self.Pid5 = "\\"
        self.Pid6 = "\\"
        self.Properties = []

        # QCResultModel object list
        self.ResultList = []
        self.InstrumentName = ""

    def AddResult(self,model):
        self.ResultList.append(model)

    def FormatForUpload(self,strInstrumentName,msgFlag,strTestTime):
        lstUploadData = []

        uploadHeader = "InstrumentList\t" + strInstrumentName
        uploadFields = "TableData\tInstrumentID\tTimeID\tTestTime\tQC_ValidDate\tQC_SN"
        uploadFieldTypes = "\tSN\tSN\tSN\tSN\tSN"
        uploadValues = "\t{}\t{}\t{}\t{}\t{}".format(strInstrumentName,strTestTime,strTestTime,"\\","\\")

        fixedUploadFields = ""
        fixedUploadFieldTypes = ""
        fixedUploadValues = ""

        for p in self.Properties:
            if p[2] == 1:
                fixedUploadFields += "\t" +  p[0]
                fixedUploadFieldTypes += "\tSN"
                fixedUploadValues += "\t" + p[1]

        results = ""
        print('Result Count:',len(self.ResultList))
        for r in self.ResultList:
            resultFields = ""
            resultFieldTypes = ""
            resultValues = ""
            for rp in r.Properties:
                if rp[2] == 1:
                    resultFields += "\t" + rp[0]
                    resultFieldTypes += "\tSN"
                    resultValues += "\t" + rp[1]

            results = results + uploadValues + fixedUploadValues + resultValues + "\r"
            print(uploadValues + fixedUploadValues + resultValues)

            uploadString = uploadHeader + "\r" + uploadFields + fixedUploadFields + resultFields + "\r" + uploadFieldTypes + fixedUploadFieldTypes + resultFieldTypes + "\r" + uploadValues + fixedUploadValues + resultValues + "\rMessageID\t" + msgFlag + "\r"
            lstUploadData.append(uploadString)

        # uploadString = uploadHeader + "\r" + uploadFields + fixedUploadFields + resultFields + "\r" + uploadFieldTypes + fixedUploadFieldTypes + resultFieldTypes + "\r" + results + "MessageID\t" + msgFlag
        # lstUploadData.append(uploadString)

        return lstUploadData