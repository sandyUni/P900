# -*- code: utf-8 -*-
import sys
import serial
import time 
import argparse
import os
from humanfriendly import parse_size
import thread
import random
# global settings may include: 
    # datatransmitedEnabled
    # dataTransmited
    # dataTransmitStartTime
    # dataTransmitNowTime
    # dev
    # blockedTransmit 

globalSettings =dict()
def speedoutput(args):
    global globalSettings
    if  globalSettings['datatransmitEnable']:
        dataTransmitedQuene5 = list()
        lastdataTransmited   = 0 
    dataRevQuene5 = list()
    lastreceivedDataAmount = 0
    while True:
        if globalSettings['work'] == False:
            return 0
        timeNow  =  time.time()
        if globalSettings['datatransmitStarted']:
            dataTransmited = globalSettings['dataTransmited']
            dataTransmitedQuene5.insert(0,dataTransmited-lastdataTransmited)
            if len(dataTransmitedQuene5)>5:
                dataTransmitedQuene5.pop()
            transmitStartTime = globalSettings['transmitStartTime']
            totalSpeed = dataTransmited/(timeNow-transmitStartTime)
            currentSpeed5=sum(dataTransmitedQuene5)/len(dataTransmitedQuene5)
            print 'transmitSpeed/currentSpeed::%.3f Bytes/s (%.3f);dataAmount: %d'%(totalSpeed,currentSpeed5,dataTransmited)
            lastdataTransmited = dataTransmited
        
        receivedDataAmount  = globalSettings['receivedDataAmount']
        dataRevQuene5.insert(0,receivedDataAmount-lastreceivedDataAmount)
        if len(dataRevQuene5)>5:
                dataRevQuene5.pop()
        currentRecSpeed5=sum(dataRevQuene5)/len(dataRevQuene5)

        dataSpeed = receivedDataAmount / (timeNow-globalSettings['startTime'])
        print 'dataSpeed/(rts):%.3f Bytes/s (%.3f);dataAmount: %d'%(dataSpeed,currentRecSpeed5,receivedDataAmount)
        lastreceivedDataAmount = receivedDataAmount
        time.sleep(1)

def readThread(args):
    f = open(args['outputfile'],'w')
    receivedDataAmount = 0 
    while True:
        if globalSettings['work'] == False:
            f.close()
            return 0
        inputSize = globalSettings['dev'].inWaiting()
        receivedDataAmount = receivedDataAmount + inputSize
        data = globalSettings['dev'].read(inputSize)
        f.write(data)
        now  = time.time()
        globalSettings['receivedDataAmount'] = receivedDataAmount 
        time.sleep(0.1)

def transmitThread(args):
    global globalSettings
    time.sleep(args['transmitdelay'])
    transmitEnable = True
    startTime = time.time()
    sleepTime = 0.01
    bufferPoint  = 0  
    haveDatatoTrans = True
    transmitTimes = 0
    dataTransmited = long(0)
    globalSettings['dataTransmited'] = dataTransmited
    if args['blocked'] or (args['randomMax'] is None) == False or (args['transmitFreq'] is None) ==False:
        blockedTransmit = True
    else:
        blockedTransmit = False

    expectedSpeed = parse_size(args['transmitSpeed'],binary=True)

    if (args['inputfile'] is None) == False:
        if inputfileSize < 10000:
            if inputfileSize == 0:
                transmitEnable = False
            transmitdataBuffer =  inputf.read()
            inputf.close()
            dataBuffered = True
            bufferPoint  = 0 
        else:
            if blockedTransmit == True:
                raise Exception('File is too large to transmit blockly(should small than 10kB)')
            dataBuffered = False
    else:
        transmitdataBuffer = args['transmitStr']
        dataBuffered = True
        bufferPoint = 0
    globalSettings['transmitStartTime'] == time.time()
    time.sleep(0.1)
    while True:
        if globalSettings['work'] == False:
            return 0
        if transmitEnable and haveDatatoTrans:
            globalSettings['datatransmitStarted'] = True
            if args['zeroBuffer']:
                bufferThreshold = 0
            else:
                bufferThreshold = 1000
            # print "out_wait:%d"%(globalSettings['dev'].out_waiting)
            if globalSettings['dev'].out_waiting <= bufferThreshold:
                data = None
                if blockedTransmit:
                    data = transmitdataBuffer
                    transmitTimes = transmitTimes +1 
                    if transmitTimes ==  args['number']:
                        haveDatatoTrans = False
                        sleepTime = 0.1
                    else:
                        if (args['transmitFreq'] is None) ==False:
                            sleepTime = 1.0 / args['transmitFreq']
                        elif (args['randomMax'] is None ) == False:
                            sleepTime = 1.0/random.uniform(args['randomMin'],args['randomMax'])
                        elif (args['transmitSpeed'] is None)  == False:
                            nowtime = time.time()
                            datalen = len(data)
                            sleepTime =max(0.001,float(dataTransmited+datalen)/expectedSpeed - (nowtime-startTime))
                        else:
                            sleepTime = 1.0
                else:
                    nowtime = time.time()
                    curentSpeed =float(dataTransmited)/( nowtime-startTime)
                    transmitChunk = 320
                    if curentSpeed < expectedSpeed: #transmit data
                        if dataBuffered:
                            if bufferPoint+transmitChunk <= len(transmitdataBuffer):
                                data = transmitdataBuffer[bufferPoint:(bufferPoint+transmitChunk)]
                                bufferPoint = bufferPoint +transmitChunk
                            else:
                                transmitTimes = transmitTimes +1 
                                if transmitTimes < args['number']:
                                    data = transmitdataBuffer[bufferPoint:len(transmitdataBuffer)]
                                    while True:
                                        dataWantedLen = transmitChunk - len(data)
                                        if dataWantedLen > len(transmitdataBuffer):
                                            data = data + transmitdataBuffer
                                            transmitTimes = transmitTimes + 1 
                                            if transmitTimes == args['number']:
                                                break
                                        else:
                                            break
                                    if transmitTimes != args['number']: 
                                        data = data + transmitdataBuffer[0:dataWantedLen]
                                        bufferPoint = dataWantedLen
                                    else:
                                        haveDatatoTrans = False
                                else:
                                    data = transmitdataBuffer[bufferPoint:len(transmitdataBuffer)]
                                    haveDatatoTrans = False
                        else:
                            tmpdata = inputf.read(transmitChunk)
                            if len(tmpdata)!=0:
                                data = tmpdata
                            else:
                                transmitTimes = transmitTimes + 1 
                                if transmitTimes<args['number']:
                                    inputf.seek(0)
                                    data = tmpdata +inputf.read(transmitChunk-len(tmpdata))
                                else:
                                    haveDatatoTrans = False
                if (data is None) == False:
                    dev.write(data)
                    # print bufferThreshold
                    
                    dataTransmited=dataTransmited + len(data)
                    globalSettings['dataTransmited']=dataTransmited
        elif transmitEnable ==True and haveDatatoTrans == False:
            transmitEnable = False
            globalSettings['datatransmitStarted'] = False
            print 'data transmitted'
            return (0)
        time.sleep(sleepTime)

        
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
                    help='transmit string')
    parser.add_argument('-k','--blocked',dest='blocked',default= False,action='store_const',                          const=True, help='tranmit data blockly, instead of streamly')
    parser.add_argument('-d','--delay',type=float,dest='transmitdelay',default= 5.0,
                    help='transmit delay, default 5s')
    parser.add_argument('-f','--freq',type=float,dest='transmitFreq',
                    help='transmit frequency for transmit string. If this argument is set, BLOCKED will aumatically be set to True')
    parser.add_argument('--random-max',type=float,dest='randomMax',help='the max frequency in the randomly-transmit mode')
    parser.add_argument('--random-min',type=float,dest='randomMin',help='the minimum frequency in the randomly-transmit mode')
    parser.add_argument('-z','--zero',dest='zeroBuffer',default= False,action='store_const',                          const=True, help='send new data untill buffer is empty, default: False')
    args = parser.parse_args()
    print args
    #some argument constraints should be added SS
    if (args.randomMin is None)!=True:
        if args.randomMax is None:
            raise Exception('--random-max and --random-min should be defined simultaneously')
        elif (args.transmitFreq is None) == False:
            raise Exception('--random-max and --random-min are isolated by -f')
    elif (args.randomMax is None)!=True:
        raise Exception('randomMax and randomMin should be defined simultaneously')
    
    # some initialization
    globalSettings['datatransmitStarted'] = False


    filename = args.outputfile
    if filename is None:
        raise Exception('Should give me a file to save data')
    
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
    
    port = str(args.comport)
    # try:
    if sys.platform == 'win32':
        device = 'COM'+port
    else:
        device = '/dev/ttyUSB'+port
    dev = serial.Serial(device,args.baudrate)
    globalSettings['dev'] = dev

    startTime = time.time()
    globalSettings['startTime']=startTime
    globalSettings['work'] = True
    globalSettings['transmitStartTime'] = startTime

    # convert args to tuple
    argsDictTuple = tuple([vars(args)])
    print argsDictTuple
    globalSettings['receivedDataAmount'] = 0 
    thread.start_new_thread(readThread,argsDictTuple)
    

    if transmitEnable:
        thread.start_new_thread(transmitThread,argsDictTuple)
        globalSettings['datatransmitEnable'] = True
    else:
        globalSettings['datatransmitEnable'] = False
    thread.start_new_thread(speedoutput,argsDictTuple)
    try:
        while True:
            time.sleep(1)
            
    except:
        globalSettings['work'] = False