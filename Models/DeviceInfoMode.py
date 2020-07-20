
class DeviceInfoModel:
    def __init__(self):
        self.DeviceID = -1
        self.DeviceName = ''
        self.DeviceSerialNo = ''
        self.DeviceLocation = ''
        self.ServerIP = ''
        self.ServerPort = ''
        self.ConnToServerTimeOut = 0

    def InitDeviceInfo(self,nDeviceID,strDeviceName,strDeviceSerialNo,strDeviceDesc,strDeviceLocation,strServerIP,nServerPort, fTimeOut):
        self.DeviceID = nDeviceID
        self.DeviceName = strDeviceName
        self.DeviceSerialNo = strDeviceSerialNo
        self.DeviceLocation = strDeviceLocation
        self.ServerIP = strServerIP
        self.ServerPort = nServerPort
        self.ConnToServerTimeOut = fTimeOut