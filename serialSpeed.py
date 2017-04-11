# -*- code: utf-8 -*-
import sys
import serial
import time 
if __name__ == '__main__':
    f = open('1.log','w')
    try:
        port = '0'
        if sys.platform == 'win32':
            device = 'COM'+port
        else:
            device = '/dev/ttyUSB'+port
        dev = serial.Serial(device,115200)
        startTime = time.time()
        receivedDataAmount =0 
        secondSegment =  0 
        while True:
            secondSegment = secondSegment +1 
            time.sleep(0.1)
            inputSize = dev.inWaiting()
            receivedDataAmount = receivedDataAmount + inputSize
            data = dev.read(inputSize)
            f.write(data)
            now  = time.time()
            dataSpeed = receivedDataAmount/(now-startTime)
            if(secondSegment==10):
                secondSegment = 0
                print 'dataSpeed:%.3f Bytes/s;dataAmount: %d'%(dataSpeed,receivedDataAmount)
    except:
        f.close()