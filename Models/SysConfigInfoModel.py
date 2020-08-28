import datetime

class SysConfigInfo:
    def __init__(self,nSaveLog,nTerminalID,nTimeSequence,nRetryTimes,nDataKeptDays,strLastDataCleanDate):
        self.SaveLog = nSaveLog > 0
        self.TerminalID = nTerminalID
        self.TimeSequence = nTimeSequence
        self.RetryTimes = nRetryTimes
        self.DataKeptDays = nDataKeptDays
        self.LastDataCleanDate = datetime.datetime.strptime(strLastDataCleanDate, '%Y-%m-%d').date()
