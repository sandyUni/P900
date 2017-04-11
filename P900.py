# -*- code: utf-8 -*-
import subprocess as sub
import serial
from serial.tools.list_ports import  comports
import re
import time 
import sys
import json
class P900(object):
    '''
        P900 devices 
    '''    
    def __init__(self,port,settings=None):
        if settings is None:
            settings  = {'baudrate':57600}
        if isinstance(port,int):
            port = str(port)
        if sys.platform == 'win32':
            device = 'COM'+port
        else:
            device = '/dev/ttyUSB'+port
        
        if settings.has_key('timeout') != True:
            settings['timeout'] = 1.5
        try:
            self.dev = serial.Serial(device,settings['baudrate'],timeout = settings['timeout'])
        except:
            print 'Some errors happens, check your permission for and device avaliability'
        
        self.isInConfigMode = False

    def enterConfigMode(self): 
        '''
            get into config mode
        '''
        if self.isInConfigMode:
            return 0
        else:
            self.dev.flushInput()
            self.dev.write('+++')
            time.sleep(3)
            inputSize = self.dev.inWaiting()
            data = self.dev.read(inputSize)
            print data
            if data.find('NO CARRIER\r\nOK')!=-1:
                print 'shake hands seccessfully.'
                self.isInConfigMode = True
                return 0
            else:
                return -1
    def leaveConfigMode(self):
        if self.isInConfigMode == False:
            return 0
        else:
            self.dev.flushInput()
            self.dev.write('ata\r\n')
            time.sleep(1)
            inputSize = self.dev.inWaiting()
            data = self.dev.read(inputSize)
            print data
            if data.find('OK')!=-1:
                print 'leave config mode seccessfully'
                self.isInConfigMode = False
                return 0
            else:
                return -1

    def setmode(self,modesettings):
        '''
            set the modesettings
            modesettings is a dict may consist of
                'networkType':'mesh' 'pp' 'pmp' 
                'workMode': in mesh type, it may be 'primary', 'slave',
                            in pp, it may be 'master', 'slave','repeater'
                            in pmp it may be 'master', 'slave','repeater'
                'networkAdress': a int string with length of 10
                'baudrate': 230400 (0)
                            115200
                            57600
                            38400
                            28800
                            19200
                            14400
                            9600 (7)  are avaiable
                 'unitAddress': string 1~255 (?)    
                 'destAddress': string 1~255 (?) or 'all'
                 'wirelessRate': Wireless Link Rate 
                            172800  (0)
                            230400
                            276480
                            57600
                            115200  (4)
                 'channelAccess':
                            'aloha'
                            'rts/cts'
                            'tdma'
                 'repeatInterval': 0-255 (indicates the channel access randomness only useful when channelAccess is set to aloha)
                 'alohaSlots': 0-255
                 'tdmaSlots' : 1-255
                 'extraCommands': list of extra commands, e.g, ['ATS109=9']

           TODO 1.support pp configuration
                2.support p2p configuration in mesh (Destination Address in mesh) 
                3.support time sync(mesh)
                4.support route enable
                5.support retransmission
                6.support coordinator rank

        '''
        baudRateTable = {'230400' :'0','115200':'1','57600':'2','38400':'3','28800':'4','19200':'5','14400':'6','9600':'7'}
        wirelessRateTable={
            '172800':'0',  
            '230400':'1',
            '276480':'2',
            '57600':'3',
            '115200':'4'
        }
        channelAccessTable ={
            'aloha':'0',
            'rts/cts':'1',
            'tdma':'2'
        }
        if self.enterConfigMode() == 0:
            self.dev.write('at&v\r\n')
            time.sleep(3)
            inputSize = self.dev.inWaiting()
            data = self.dev.read(inputSize)
            print data

            commandlines = list()

            # factorCommand and unit address, destination address
            factorCommand = None
            destAddressCommand = None
            unitAddressCommand =None
            baudRateCommand = None
            wirelessRateCommand = None
            networkAdressCommand  = None
            channelAccessModeCommand= None
            repeatIntervalCommand  = None
            alohaSlotsCommand   = None
            tdmaSlotsCommand  = None
            networkType = modesettings['networkType']

            if networkType == 'pmp':
                workmode = modesettings['workMode']
                if workmode == 'master':
                    factorCommand = 'AT&F7'
                    if modesettings.has_key('destAddress'):
                        if modesettings['destAddress'] == 'all':
                            destAddressCommand = 'ATS140=65535'
                        else:
                            destAddressCommand = 'ATS140='+modesettings['destAddress']
                elif workmode == 'slave':
                    factorCommand = 'AT&F8'
                    unitAddressCommand = 'ATS105='+modesettings['unitAddress']

            elif networkType == 'pp':
                pass
            elif networkType  == 'mesh':
                workmode = modesettings['workMode']
                if workmode == 'primary':
                    factorCommand = 'AT&F1'
                elif workmode == 'slave':
                    factorCommand = 'AT&F2'
                
                if modesettings.has_key('channelAccess'):
                    tmpStr =modesettings['channelAccess'].lower()
                    channelAccessModeCommand = 'ATS244='+channelAccessTable[tmpStr]
                
                if modesettings.has_key('repeatInterval'):
                    repeatIntervalCommand = 'ATS115='+modesettings['repeatInterval']
                
                if modesettings.has_key('alohaSlots'):
                    alohaSlotsCommand = 'ATS214='+modesettings['alohaSlots']

                if modesettings.has_key('tdmaSlots'):
                    tdmaSlotsCommand = 'ATS221='+modesettings['tdmaSlots']

            if factorCommand is None:
                print 'not support yet, do nothing'
                return
            if modesettings.has_key('baudrate'):
                baudRateCommand = 'ATS102='+baudRateTable[modesettings['baudrate']]
            else:
                baudRateCommand = 'ATS102='+baudRateTable[str(self.dev.baudrate)]
            if modesettings.has_key('wirelessRate'):
                wirelessRateCommand = 'ATS103='+ wirelessRateTable[modesettings['wirelessRate']]
            if modesettings.has_key('networkAdress'):
                networkAdressCommand = 'ATS104='+ modesettings['networkAdress']
            
            
            commandlines = [factorCommand]
            if (destAddressCommand is None) == False:
                commandlines.append(destAddressCommand)
            if (unitAddressCommand is None) == False:
                commandlines.append(unitAddressCommand)
            if (baudRateCommand is None) == False:
                commandlines.append(baudRateCommand)
            if (wirelessRateCommand is None) == False:
                commandlines.append(wirelessRateCommand)
            if (networkAdressCommand is None) == False:
                commandlines.append(networkAdressCommand)
            if (channelAccessModeCommand is None) == False:
                commandlines.append(channelAccessModeCommand)    
            if (repeatIntervalCommand is None) == False:
                commandlines.append(repeatIntervalCommand) 
            if (alohaSlotsCommand is None) == False:
                commandlines.append(alohaSlotsCommand)
            if (tdmaSlotsCommand is None) == False:
                commandlines.append(tdmaSlotsCommand)
            
            if modesettings.has_key('extraCommands'):
                extraCommands = '\r\n'.join(modesettings['extraCommands'])+ '\r\n'
                command = '\r\n'.join(commandlines) +'\r\n'+ extraCommands +'at&w\r\n'
            else:
                command = '\r\n'.join(commandlines) +'\r\n' +'at&w\r\n'

            self.dev.write(command)
            time.sleep(3)
            inputSize = self.dev.inWaiting()
            data = self.dev.read(inputSize)
            print data

            self.dev.write('at&v\r\n')
            time.sleep(3)
            inputSize = self.dev.inWaiting()
            data = self.dev.read(inputSize)
            print data

            self.leaveConfigMode()
            return data
        else:
            print 'check your device settings'

        
if __name__ =='__main__':
    # aP900 = P900(2,{'baudrate':57600})
    aP900 = P900(3,{'baudrate':57600})
    # modesettings = {'networkType':'pmp', 
    #             'workMode': 'master',
    #             'wirelessRate':'276480',
    #             'networkAdress': '2234567123',
    #             'baudrate':'57600'}
    modesettings = {'networkType':'pmp', 
                'workMode': 'slave',
                'unitAddress':'33',
                'networkAdress': '2234567123',
                'wirelessRate':'276480',
                'baudrate':'57600'}
    # modesettings = {'networkType':'pmp', 
    #             'workMode': 'slave',
    #             'unitAddress':'11',
    #             'networkAdress': '1234567123',
    #             'wirelessRate':'276480',
    #             'baudrate':'57600',
    #             'extraCommands':['ATS109=9','ATS180=3']}
    
    # Mesh Primary
    # modesettings = {'networkType':'mesh', 
    #                 'workMode': 'primary',
    #                 'networkAdress': '1234567891',
    #                 'baudrate':'57600',
    #                 'channelAccess':'tdma',
    #                 'tdmaSlots' : '1'
    #                 }
    # mesh slave 
    # modesettings = {'networkType':'mesh', 
    #                 'workMode': 'slave',
    #                 'networkAdress': '1234567891',
    #                 'baudrate':'57600',
    #                 'channelAccess':'tdma',
    #                 'tdmaSlots' : '3'
    #                 }
    aP900.setmode(modesettings)