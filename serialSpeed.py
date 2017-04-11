# -*- code: utf-8 -*-
import sys
import serial
import time 
import argparse
import os
from humanfriendly import parse_size
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Measure serial port speed and data log')
    parser.add_argument('comport', type=int,
                    help='an integer for the serial port')
    parser.add_argument('-b','--baudrate', dest='baudrate',type=int,default=57600,
                    help='baudrate(default 57600)')
    parser.add_argument('-o','--output', dest='outputfile', 
                    help='output file name')
    parser.add_argument('-i','--input', dest='inputfile', 
                    help='input file name, will transfer the data using a given speed')
    parser.add_argument('-s','--speed',dest='transmitSpeed',default = '1k',
                    help='transmit speed, support: 1k,1000(B), default:1kB/s')
    parser.add_argument('-n','--number',type=int, dest='number',default=1,
                    help='transmit times, default:1')
    parser.add_argument('-t','--transmit',type=str,dest='transmitStr',
                    help='transmit string' )
    parser.add_argument('-d','--delay',type=float,dest='transmitdelay',default= 5.0,
                    help='transmit delay, default 5s' )
    args = parser.parse_args()

    
    print args
    filename = args.outputfile
    if filename is None:
        raise Exception('Should give me a file to save data')
    f = open(filename,'w')

    inputf = None
    transmitEnable = False
    if (args.inputfile is None) == False:
        if os.path.isfile(args.inputfile):
            inputfileSize = os.path.getsize(args.inputfile)
            inputf = open(args.inputfile,'r')
            transmitEnable = True
        else:
            raise Exception('input file not found') 
    if (args.transmitStr is None) == False:
        if transmitEnable == True:
            raise Exception('Don\'t support transmit string and file simultaneously')
        transmitEnable = True
    
    if transmitEnable == True:
        expectedSpeed = parse_size(args.transmitSpeed,binary=True)

    port = str(args.comport)
    # try:
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
    haveDatatoTrans = True
    transmitTimes   = 0
    dataBuffered = False
    if (args.inputfile is None) == False:
        if inputfileSize < 10000:
            if inputfileSize == 0:
                transmitEnable = False
            transmitdataBuffer =  inputf.read()
            inputf.close()
            dataBuffered = True
            bufferPoint  = 0 
        else:
            dataBuffered = False
    else:
        transmitdataBuffer = args.transmitStr
        dataBuffered = True
        bufferPoint = 0

    dataTransmited = long(0)
    startTime = time.time()
    transmitStart = False 
    while True:
        if transmitStart ==False:
            thisTime = time.time()
            if thisTime-  startTime > args.transmitdelay:
                transmitStart = True
                startTime = thisTime
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
            if transmitEnable and haveDatatoTrans and transmitStart:
                nowtime = time.time() 
                curentSpeed =float(dataTransmited)/( nowtime-startTime)
                print 'current transmit speed: %0.3f'%curentSpeed
        if transmitEnable and haveDatatoTrans and transmitStart:
            if dev.out_waiting<100:
                nowtime = time.time()
                curentSpeed =float(dataTransmited)/( nowtime-startTime)
                if curentSpeed < expectedSpeed: #transmit data
                    data = None
                    if dataBuffered:
                        if bufferPoint+100 <= len(transmitdataBuffer):
                            data = transmitdataBuffer[bufferPoint:(bufferPoint+100)]
                            bufferPoint = bufferPoint +100-1
                        else:
                            transmitTimes = transmitTimes +1 
                            if transmitTimes < args.number:
                                data = transmitdataBuffer[bufferPoint:len(transmitdataBuffer)]
                                while True:
                                    dataWantedLen = 100 - len(data)
                                    if dataWantedLen > len(transmitdataBuffer):
                                        data = data + transmitdataBuffer
                                        transmitTimes = transmitTimes + 1 
                                        if transmitTimes == args.number:
                                            break
                                    else:
                                        break
                                if transmitTimes != args.number: 
                                    data = data + transmitdataBuffer[0:dataWantedLen]
                                    bufferPoint = dataWantedLen
                                else:
                                    haveDatatoTrans = False
                            else:
                                data = transmitdataBuffer[bufferPoint:len(transmitdataBuffer)]
                                haveDatatoTrans = False
                    else:
                        tmpdata = inputf.read(100)
                        if len(tmpdata)!=0:
                            data = tmpdata
                        else:
                            transmitTimes = transmitTimes + 1 
                            if transmitTimes<args.number:
                                inputf.seek(0)
                                data = tmpdata +inputf.read(100-len(tmpdata))
                            else:
                                haveDatatoTrans = False
                    if (data is None) == False:
                        dev.write(data)
                        dataTransmited=dataTransmited + len(data)
        elif transmitEnable ==True and haveDatatoTrans == False:
            transmitEnable = False
            print 'data transmitted'

    # except exce: 
    #     print 'exiting:',exce   
    #     if (args.inputfile is None) == False and dataBuffered ==False:
    #         inputf.close() 
    #     f.close()