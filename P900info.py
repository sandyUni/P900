# -*- code: utf-8 -*-
import P900
import json
import time 
if __name__ == '__main__':
    aP900 = P900.P900(3,{'baudrate':115200})
    if aP900.enterConfigMode()==0:
        aP900.dev.write('at&v\r\n')
        time.sleep(3)
        inputSize = aP900.dev.inWaiting()
        data = aP900.dev.read(inputSize)
        print data
        aP900.leaveConfigMode()
    else:
        raise Exception('check your device settings')