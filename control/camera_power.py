# 2020.6.2
# v1.0 by mengjun
# camera power on and off ;read power

import sys
import time
import serial
import binascii
import argparse

comport0 = '/dev/ttyUSB0'
comport1 = '/dev/ttyUSB1'
baud = 115200
return_data,shijian,latit, longit = 0,0,0,0

try:
    ser = serial.Serial(comport1, baud)
except Exception as e:
    # if ser.isOpen() == False:
    ser = serial.Serial(comport0, baud)

def parse_args():
    desc = ('camer power')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--up', dest='power_up', action='store_true')
    parser.add_argument('--down', dest='power_down', action='store_true')
    parser.add_argument('--read_power', dest='power_read', action='store_true')
    parser.add_argument('--read_gps', dest='gps_read', action='store_true')
    args = parser.parse_args()
    return args

# power up
def up():
    up = bytearray.fromhex('01 10 00 E0 FF 00 55 AA')
    ser.write(up)
    time.sleep(0.1)
    return True

# power down
def down():
    down = bytearray.fromhex('01 10 00 E0 00 00 55 AA')
    ser.write(down)
    time.sleep(0.1)
    return True
    
# power read
def power_read():
    power = bytearray.fromhex('01 03 00 F0 00 01 55 AA')
    ser.write(power)
    time.sleep(0.1)
    len_return_data = ser.inWaiting()

    if len_return_data:
        return_data = ser.read(len_return_data)
        return_data = binascii.b2a_hex(return_data)
        return_data = str(return_data[6:10])[2:6]
        power = int(return_data, 16)
    return power

# gps read
def gps_read():
    gps = bytearray.fromhex('01 03 00 05 00 23 14 12')
    ser.write(gps)
    time.sleep(0.1)
    len_return_data = ser.inWaiting()
    global return_data,shijian,latit,longit
    if len_return_data:
        return_data = ser.read(len_return_data)
        
        if len(str(return_data).split(',')) < 4:
            return return_data,shijian,latit,longit

        # time +8
        shijian = str(return_data).split(',')[1]
        # N
        latit = str(return_data).split(',')[2]
        # E
        longit = str(return_data).split(',')[4]

    return return_data,shijian,latit, longit





