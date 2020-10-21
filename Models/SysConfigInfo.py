import datetime

class SysConfigInfo:
    
    def __init__(self,nSaveLog,nTerminalID,nTimeSequence,nRetryTimes,nDataKeptDays,strLastDataCleanDate):
        self.SaveLog = nSaveLog > 0
        self.TerminalID = nTerminalID
        self.TimeSequence = nTimeSequence
        self.RetryTimes = nRetryTimes
        self.DataKeptDays = nDataKeptDays
        strDate = strLastDataCleanDate[0:10]
        self.LastDataCleanDate = datetime.datetime.strptime(strDate,'%Y-%m-%d').date()
        print('OK2')
    
    def toJson(self):
        sysJson = {}
        sysJson["SaveLog"] = self.SaveLog
        sysJson["TerminalID"] = self.TerminalID
        sysJson["TimeSequence"] = self.TimeSequence
        sysJson["RetryTimes"] = self.RetryTimes
        sysJson["DataKeptDays"] = self.DataKeptDays
        sysJson["LastDataCleanDate"] = self.LastDataCleanDate
        return sysJson
