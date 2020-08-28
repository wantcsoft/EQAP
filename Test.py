import serial
import time

import time
import queue
import datetime
from threading import Thread
import socket
import select
import sqlite3
from Crypto.Cipher import AES



ss = serial.Serial('/dev/ttyXRUSB0', 115200, timeout=0.02)

while True:
    if ss.inWaiting() > 0:
        print('Com port receive data:')
        print(ss.readline())
    else:
        time.sleep(1)

# import sqlite3
#
# conn = sqlite3.connect('/home/projects/EQAP/DB/Eqap.DB')
# # sqlCmdTxt = ''' '''
# sqlCmdTxt = '''SELECT * FROM BSC_BasicProtocolFieldInfo'''
# result = conn.execute(sqlCmdTxt).fetchall()
# print(result)
