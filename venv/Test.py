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

ss = serial.Serial('/dev/ttyO3',115200,timeout=0.02)

while True:
    if ss.inWaiting() > 0:
        print('Com port receive data:',ss.readline())
    else:
        time.sleep(1)
