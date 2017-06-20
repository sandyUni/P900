# -*- code: utf-8 -*-
import sys
from serial.tools.list_ports import comports
if __name__ =='__main__':
    devices = comports()
    if sys.platform == 'win32':
        for device in devices:
             print device.device,':',device.description,'\n   hwid:',device.hwid
        print "%d port(s) found"%(len(devices))
    else:
        validDevices=0 
        for device in devices:
            if device[0].find('USB')!=-1 or device[0].find('ACM')!=-1:
                validDevices = validDevices + 1 
                print device[0],':',device[1],'\n  VID:',device[2]
        print "%d port(s) found"%(validDevices)
    raw_input("Press the <ENTER> key to continue...")