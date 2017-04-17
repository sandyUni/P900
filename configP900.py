# -*- code: utf-8 -*-
import P900
import json

filename = 'P900Config.json'
f = open(filename,'r')
jsonSetting = json.load(f)
print jsonSetting