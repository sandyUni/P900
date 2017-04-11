# -*- code: utf-8 -*-
import sys
import serial
import time 
import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Measure serial port speed and data log')
    parser.add_argument('comport', type=int, nargs='+',
                    help='an integer for the serial port')
    parser.add_argument('-b','--baudrate', dest='baudrate',type=int,default=57600,
                    help='baudrate(default 57600)')
    parser.add_argument('-o','--output', dest='outputfile', nargs='+',
                    help='output file names')
    args = parser.parse_args()
    filename = args.outputfile[0]
    f = open(filename,'w')
    port = str(args.comport[0])
    try:
        if sys.platform == 'win32':
            device = 'COM'+port
        else:
            device = '/dev/ttyUSB'+port
        dev = serial.Serial(device,args.baudrate)
        startTime = time.time()
        receivedDataAmount =0 
        secondSegment =  0 
        lastSecond = startTime
        receivedDataAmountSecond = 0
        while True:
            secondSegment = secondSegment +1 
            time.sleep(0.1)
            inputSize = dev.inWaiting()
            receivedDataAmount = receivedDataAmount + inputSize
            receivedDataAmountSecond  = receivedDataAmountSecond + inputSize
            data = dev.read(inputSize)
            f.write(data)
            now  = time.time()
            dataSpeed = receivedDataAmount/(now-startTime)
            if(secondSegment==10):
                secondTime = time.time() 
                secondSegment = 0
                print 'dataSpeed/(rts):%.3f Bytes/s (%.3f);dataAmount: %d'%(dataSpeed,(receivedDataAmountSecond)/(secondTime-lastSecond),receivedDataAmount)
                lastSecond = secondTime
                receivedDataAmountSecond =0 
    except:     
        f.close()