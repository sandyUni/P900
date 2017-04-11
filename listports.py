# -*- code: utf-8 -*-
import sys
from serial.tools.list_ports import comports
if __name__ =='__main__':
    devices = comports()
    devNames= list()
    for device in devices:
        devNames.append(device.name)
    
    if sys.platform == 'win32':
        for device in devices:
             print device.device,':',device.description,'\n   hwid:',device.hwid
        print "%d port(s) found"%(len(devices))
    else:
        validDevices=0 
        for device in devices:
            if device.device.find('USB')!=-1 or device.device.find('ACM')!=-1:
                validDevices = validDevices + 1 
                print device.device,':',device.description,'\n   hwid:',device.hwid