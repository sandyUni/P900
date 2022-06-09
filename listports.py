'''
Author: Lai Jun
E-mail: laijun@nudt.edu.cn
LastEditors: Lai Jun
LastEditTime: 2022-06-09 12:16:14
'''
# -*- code: utf-8 -*-
import sys
import serial
from serial.tools.list_ports import comports
if __name__ =='__main__':
    devices = comports()
    if sys.platform == 'win32':
        for device in devices:
             print(device.device,':',device.description,'\n   hwid:',device.hwid)
        print("%d port(s) found"%(len(devices)))
    else:
        validDevices=0 
        for device in devices:
            if device[0].find('USB')!=-1 or device[0].find('ACM')!=-1:
                validDevices = validDevices + 1 
                print(device[0],':',device[1],'\n  VID:',device[2])
        print("%d port(s) found"%(validDevices))