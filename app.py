import json

from flask import render_template, request

import datetime
from flask import Flask
from flask_cors import *
from WebPublicMethods import PublicMethods

# p = PublicMethods('../EQAP/DB/Eqap.DB')
p = PublicMethods('./DB/Eqap.DB')
# p = PublicMethods('/home/projects/EQAP/DB/Eqap.DB')

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/')
def home():
    return render_template('index.html')


# 获取系统配置信息
@app.route('/getSystemSetup')
def getSystemSetup():
    model = p.GetSystemConfig()
    return model.toJson()


# 获取设备配置信息
@app.route('/getDeviceSetup')
def getDeviceSetup():
    device = p.GetDeviceInfoFromDB()
    return device.toJson()


# 获取仪器配置信息
@app.route('/getInstrumentSetup')
def getInstrumentSetup():
    pList = p.GetInstrumentInfoFromDB()
    return {"pList": pList}


# 获取报文设置信息
@app.route('/getProtocolConfig')
def getProtocolConfig():
    pList = p.GetProtocolList()
    return {"pList": pList}


# 获取Message
@app.route('/getMessage', methods=['Post'])
def getMessage():
    data = json.loads(request.data.decode())
    txtProtocolID = data["ProtocolID"]
    messageList = p.GetMessageList(txtProtocolID)
    return {"messageList": messageList}


# 获取Field
@app.route('/getField', methods=['Post'])
def getField():
    data = json.loads(request.data.decode())
    txtProtocolID = data["ProtocolID"]
    txtMsgID = data["MsgID"]
    fieldList = p.GetFieldList(txtProtocolID, txtMsgID)
    return {"fieldList": fieldList}


# 更新系统配置信息
@app.route('/updateSystemSetup', methods=['POST'])
def updateSystemSetup():
    try:
        data = json.loads(request.data.decode())
        txtSaveLog = data["SaveLog"]
        txtTerminalID = data["TerminalID"]
        txtDataKeptDays = data["DataKeptDays"]
        txtTimeSequence = data["TimeSequence"]
        txtRetryTimes = data["RetryTimes"]
        if txtSaveLog:
            nSaveLog = 1
        else:
            nSaveLog = 0
        print("Save Log:", nSaveLog, txtSaveLog)
        nTerminalID = int(txtTerminalID)
        nDataKeptDays = int(txtDataKeptDays)
        nTimeSequence = int(txtTimeSequence)
        nRetryTimes = int(txtRetryTimes)
        dtLastUpdate = datetime.datetime.now().date()
        print(nSaveLog, nTerminalID, nTimeSequence, nRetryTimes, nDataKeptDays, dtLastUpdate)
        p.UpdateSysConfig(nSaveLog, nTerminalID, nTimeSequence, nRetryTimes, nDataKeptDays, dtLastUpdate)
    except BaseException as e:
        print("Update system config with exception:{}".format(e))
        return {"message": "更新失败"}

    return {"message": "更新成功"}


# 更新设备配置信息
@app.route('/updateDevice', methods=['POST'])
def updateDevice():
    try:
        data = json.loads(request.data.decode())
        txtDeviceName = data["DeviceName"]
        txtDeviceSerialNo = data["DeviceSerialNo"]
        txtDeviceLocation = data["DeviceLocation"]
        txtDeviceDesc = data["DeviceDesc"]
        txtServerIP = data["ServerIP"]
        txtServerPort = data["ServerPort"]
        txtConnToServerTimeOut = data["ConnToServerTimeOut"]
        fTimeout = float(txtConnToServerTimeOut)
        txtDeviceID = data["DeviceID"]
        nDeviceID = int(txtDeviceID)
        if p.UpdateDeviceInfoToDB(nDeviceID, txtDeviceName, txtDeviceSerialNo, txtDeviceDesc, txtDeviceLocation,
                                  txtServerIP, int(txtServerPort), fTimeout):
            print('Update device info sucessfully')
        else:
            print("Update device info failed")
            return {"message": "更新失败"}
    except BaseException as e:
        print("Update device information failed")
        return {"message": "更新失败"}
    return {"message": "更新成功"}


# 跟新仪器配置信息
@app.route('/updateInstrument', methods=['POST'])
def updateInstrument():
    try:
        data = json.loads(request.data.decode())
        txtInstrumentNo = data["InstrumentNo"]
        txtInstrumentID = data["InstrumentID"]
        txtInstrumentName = data["InstrumentName"]
        txtInstrumentSerialNo = data["InstrumentSerialNo"]
        txtInstrumentDesc = data["InstrumentDesc"]
        txtInstrumentLocation = data["InstrumentLocation"]
        txtHighConcentrationID = data["HighConcentrationID"]
        txtMidConcentrationID = data["MidConcentrationID"]
        txtLowConcentrationID = data["LowConcentrationID"]
        txtProtocolID = data["ProtocolID"]
        nProtocolID = int(txtProtocolID)
        txtBaudRate = data["BaudRate"]
        nBaudRate = int(txtBaudRate)
        txtPortName = data["PortName"]
        txtIsActive = data["IsActive"]
        if txtIsActive:
            nIsActive = 1
        else:
            nIsActive = 0
        if p.UpdateInstrumentInfoToDB(txtInstrumentNo, txtInstrumentID, txtInstrumentName, txtInstrumentSerialNo,
                                      txtInstrumentDesc, txtInstrumentLocation, txtHighConcentrationID,
                                      txtMidConcentrationID, txtLowConcentrationID, nProtocolID, nBaudRate,
                                      txtPortName, nIsActive):
            print('Update instrument info successfully')
        else:
            print("Update instrument info failed")
            return {"message": "更新失败"}
    except BaseException as e:
        print("Update instrument information failed")
        return {"message": "更新失败"}
    return {"message": "更新成功"}


# 跟新报文配置信息
@app.route('/updateProtocol', methods=['POST'])
def updateProtocol():
    try:
        data = json.loads(request.data.decode())
        txtProtocolID = data["ProtocolID"]
        txtProtocolName = data["ProtocolName"]
        txtProtocolType = data["ProtocolType"]
        txtIsEnabled = data["IsEnabled"]
        if txtIsEnabled:
            nIsEnabled = 1
        else:
            nIsEnabled = 0
        p.UpdateProtocolInfo(txtProtocolID, txtProtocolName, txtProtocolType, nIsEnabled)
    except BaseException as e:
        print("ProtocolUpdate with exception {}".format(e))
        return {"message": "更新失败"}
    return {"message": "更新成功"}


# 跟新Message
@app.route('/updateMessage', methods=['POST'])
def updataMessage():
    try:
        data = json.loads(request.data.decode())
        txtMsgID = int(data["MsgID"])
        txtProtocolID = int(data["ProtocolID"])
        txtProtocolMsgType = int(data["ProtocolMsgType"])
        txtMsgHeader = data["MsgHeader"]
        txtMsgEndFlag = data["MsgEndFlag"]
        txtFieldCount = int(data["FieldCount"])
        txtUploadFormat = data["UploadFormat"]
        txtToBeUpload = int(data["ToBeUpload"])
        txtSampleIDFrom = data["SampleIDFrom"]

        p.UpdateMessageInfo(txtProtocolMsgType, txtMsgHeader, txtMsgEndFlag, txtFieldCount, txtUploadFormat,
                            txtToBeUpload, txtSampleIDFrom, txtProtocolID, txtMsgID)
    except BaseException as e:
        print("ProtocolUpdate with exception {}".format(e))
        return {"message": "更新失败"}
    return {"message": "更新成功"}


# 跟新Field
@app.route('/updateField', methods=['POST'])
def updateField():
    try:
        data = json.loads(request.data.decode())
        txtFieldID = int(data["FieldID"])
        txtProtocolID = int(data["ProtocolID"])
        txtMsgID = int(data["MsgID"])
        txtFieldName = data["FieldName"]
        txtFieldType = data["FieldType"]
        txtFieldIndex = int(data["FieldIndex"])
        txtStartPos = int(data["StartPos"])
        txtFieldLen = int(data["FieldLen"])
        txtValueRange = data["ValueRange"]
        txtToBeCleared = int(data["ToBeCleared"])
        txtIsRepeat = int(data["IsRepeat"])
        txtIsUpload = int(data["IsUpload"])

        p.UpdateFieldInfo(txtFieldName, txtFieldType, txtFieldIndex, txtStartPos, txtFieldLen, txtValueRange,
                          txtToBeCleared, txtIsRepeat, txtIsUpload, txtProtocolID, txtMsgID, txtFieldID)
    except BaseException as e:
        print("ProtocolUpdate with exception {}".format(e))
        return {"message": "更新失败"}
    return {"message": "更新成功"}


# 创建一个新的仪器配置信息
@app.route('/createInstrument', methods=['POST'])
def createInstrument():
    try:
        data = json.loads(request.data.decode())
        txtInstrumentID = data["InstrumentID"]
        txtInstrumentName = data["InstrumentName"]
        txtInstrumentSerialNo = data["InstrumentSerialNo"]
        txtInstrumentDesc = data["InstrumentDesc"]
        txtInstrumentLocation = data["InstrumentLocation"]
        txtHighConcentrationID = data["HighConcentrationID"]
        txtMidConcentrationID = data["MidConcentrationID"]
        txtLowConcentrationID = data["LowConcentrationID"]
        txtProtocolID = data["ProtocolID"]
        nProtocolID = int(txtProtocolID)
        txtBaudRate = data["BaudRate"]
        nBaudRate = int(txtBaudRate)
        txtPortName = data["PortName"]
        txtIsActive = data["IsActive"]
        if txtIsActive:
            nIsActive = 1
        else:
            nIsActive = 0
        p.SaveInstrumentInfo(txtInstrumentID, txtInstrumentName, txtInstrumentSerialNo, txtInstrumentDesc,
                             txtInstrumentLocation, txtHighConcentrationID, txtMidConcentrationID, txtLowConcentrationID,
                             nProtocolID, nBaudRate, txtPortName, nIsActive)
    except BaseException as e:
        print("InstrumentCreate with exception {}".format(e))
        return {"message": "创建失败"}
    return {"message": "创建成功"}


# 创建一个新的报文配置信息
@app.route('/createProtocol', methods=['POST'])
def createProtocol():
    try:
        data = json.loads(request.data.decode())
        txtProtocolName = data["ProtocolName"]
        txtProtocolType = data["ProtocolType"]
        if "IsEnabled" in data:
            if data["IsEnabled"]:
                nIsEnabled = 1
            else:
                nIsEnabled = 0
        else:
            nIsEnabled = 0
        p.SaveProtocolInfo(txtProtocolName, txtProtocolType, nIsEnabled)
    except BaseException as e:
        print("ProtocolCreate with exception {}".format(e))
        return {"message": "创建失败"}
    return {"message": "创建成功"}


# 创建一个新的Message配置信息
@app.route('/createMessage', methods=['POST'])
def createMessage():
    try:
        data = json.loads(request.data.decode())
        txtProtocolID = int(data["ProtocolID"])
        txtProtocolMsgType = int(data["ProtocolMsgType"])
        txtMsgHeader = data["MsgHeader"]
        txtMsgEndFlag = data["MsgEndFlag"]
        txtFieldCount = int(data["FieldCount"])
        txtUploadFormat = data["UploadFormat"]
        txtToBeUpload = int(data["ToBeUpload"])
        txtSampleIDFrom = data["SampleIDFrom"]

        p.SaveMessageInfo(txtProtocolMsgType, txtMsgHeader, txtMsgEndFlag, txtFieldCount, txtUploadFormat,
                          txtToBeUpload, txtSampleIDFrom, txtProtocolID)
    except BaseException as e:
        print("ProtocolUpdate with exception {}".format(e))
        return {"message": "创建失败"}
    return {"message": "创建成功"}


# 创建一个新的Field
@app.route('/createField', methods=['POST'])
def createField():
    try:
        data = json.loads(request.data.decode())
        txtProtocolID = int(data["ProtocolID"])
        txtMsgID = int(data["MsgID"])
        txtFieldName = data["FieldName"]
        txtFieldType = data["FieldType"]
        txtFieldIndex = int(data["FieldIndex"])
        txtStartPos = int(data["StartPos"])
        txtFieldLen = int(data["FieldLen"])
        txtValueRange = data["ValueRange"]
        txtToBeCleared = int(data["ToBeCleared"])
        txtIsRepeat = int(data["IsRepeat"])
        txtIsUpload = int(data["IsUpload"])

        p.SaveFieldInfo(txtFieldName, txtFieldType, txtFieldIndex, txtStartPos, txtFieldLen, txtValueRange,
                        txtToBeCleared, txtIsRepeat, txtIsUpload, txtProtocolID, txtMsgID)
    except BaseException as e:
        print("ProtocolUpdate with exception {}".format(e))
        return {"message": "更新失败"}
    return {"message": "更新成功"}


# 删除设备配置信息
@app.route('/deleteInstrument', methods=['POST'])
def deleteInstrument():
    try:
        data = json.loads(request.data.decode())
        txtInstrumentNo = data["InstrumentNo"]
        nInstrumentNo = int(txtInstrumentNo)
        p.DeleteInstrumentInfo(nInstrumentNo)
    except BaseException as e:
        print("InstrumentDelete with exception {}".format(e))
        return {"message": "删除失败"}
    return {"message": "删除成功"}


# 删除报文配置信息
@app.route('/deleteProtocol', methods=['POST'])
def deleteProtocol():
    try:
        data = json.loads(request.data.decode())
        txtProtocolID = data["ProtocolID"]
        p.DeleteProtocolInfo(txtProtocolID)
    except BaseException as e:
        print("ProtocolDelete with exception {}".format(e))
        return {"message": "删除失败"}
    return {"message": "删除成功"}


# 删除Message配置信息
@app.route('/deleteMessage', methods=['POST'])
def deleteMessage():
    try:
        data = json.loads(request.data.decode())
        txtMsgID = data["MsgID"]
        p.DeleteMessageInfo(txtMsgID)
    except BaseException as e:
        print("ProtocolDelete with exception {}".format(e))
        return {"message": "删除失败"}
    return {"message": "删除成功"}


# 删除Field配置信息
@app.route('/deleteField', methods=['POST'])
def deleteField():
    try:
        data = json.loads(request.data.decode())
        txtFieldID = int(data["FieldID"])
        p.DeleteFieldInfo(txtFieldID)
    except BaseException as e:
        print("ProtocolDelete with exception {}".format(e))
        return {"message": "删除失败"}
    return {"message": "删除成功"}


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
