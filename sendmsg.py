# -*- code: utf-8 -*-
import sys
import serial
import time 
if __name__ == '__main__':
    port = str(7)
    strSent  = 'this is master broadcasts for testing the link\n'
    if sys.platform == 'win32':
        device = 'COM'+port
    else:
        device = '/dev/ttyUSB'+port
    dev = serial.Serial(device,57600)
    count = 0
    while True:
        count = count +1
        dev.write(strSent)
        print(count )
        time.sleep(0.3)