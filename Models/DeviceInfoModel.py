
class DeviceInfoModel:
    def __init__(self):
        self.DeviceID = -1
        self.DeviceName = ''
        self.DeviceSerialNo = ''
        self.DeviceDesc = ''
        self.DeviceLocation = ''
        self.ServerIP = ''
        self.ServerPort = ''
        self.ConnToServerTimeOut = 0

    def InitDeviceInfo(self,nDeviceID,strDeviceName,strDeviceSerialNo,strDeviceDesc,strDeviceLocation,strServerIP,nServerPort, fTimeOut):
        self.DeviceID = nDeviceID
        self.DeviceName = strDeviceName
        self.DeviceSerialNo = strDeviceSerialNo
        self.DeviceDesc = strDeviceDesc
        self.DeviceLocation = strDeviceLocation
        self.ServerIP = strServerIP
        self.ServerPort = nServerPort
        self.ConnToServerTimeOut = fTimeOut

    def toJson(self):
        devJson = {}
        devJson["DeviceID"] = self.DeviceID
        devJson["DeviceName"] = self.DeviceName
        devJson["DeviceSerialNo"] = self.DeviceSerialNo
        devJson["DeviceDesc"] = self.DeviceDesc
        devJson["DeviceLocation"] = self.DeviceLocation
        devJson["ServerIP"] = self.ServerIP
        devJson["ServerPort"] = self.ServerPort
        devJson["ConnToServerTimeOut"] = self.ConnToServerTimeOut
        return devJson
