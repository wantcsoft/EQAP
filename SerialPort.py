import serial
from time import sleep

class SerialPort:
    def __init__(self, strPortName, nBaudRate,strInstrName,nProtocolID):
        self.com = serial.Serial(strPortName, int(nBaudRate), timeout=0.002)
        self.InstrumentName = strInstrName
        self.waitTimes = 10
        self.ProtocolID = nProtocolID
        self.PortName = strPortName
    
    def ReadLine(self):
        try:
            if self.com.isOpen() == False:
                self.com.open()

            waitIndex = 0
            while waitIndex < self.waitTimes:
                if (self.com.inWaiting() > 0):
                    print("Receive data from serial port")
                    return self.com.readline()
                sleep(0.01)
                waitIndex += 1

        except IOError as e:
            print("Read data from serial port with exception:{}".format(e))
        return ""