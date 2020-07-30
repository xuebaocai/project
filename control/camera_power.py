#2020.7.30
#v1.1 by mengjun
#camera power on and off ;read power
#crontab  * * * * * /usr/bin/python3 /home/mengjun/project/control/camera_power.py --up

import sys
import time
import serial    #apt-get python3-serial
import binascii
import argparse

comport0 = '/dev/ttyUSB0'
comport1 = '/dev/ttyUSB1'
baud = 11600

try:
    ser = serial.Serial(comport0, baud)
except:
    ser = serial.Serial(comport1,baud)

#print(ser.isOpen())

def parse_args():
    desc = ('camer power')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--up',dest='power_up',action='store_true')
    parser.add_argument('--down',dest='power_down',action='store_true')
    parser.add_argument('--power_read',dest='power_read',action='store_true')
    parser.add_argument('--gps_read', dest='gps_read', action='store_true')
    args = parser.parse_args()
    return args

#power up
def up():
    up = bytearray.fromhex('01 10 00 E0 FF 00 55 AA')
    ser.write(up)
    time.sleep(0.1)
    '''
    print('up done')
    with open ('/home/mengjun/project/control/record.txt','w+') as f:
        f.write('haha')
    '''
    return True

#power down
def down():
    down = bytearray.fromhex('01 10 00 E0 00 00 55 AA')
    ser.write(down)
    time.sleep(0.1)       
    #print('down done')
    return True

#power read
def power_read():
    power = bytearray.fromhex('01 03 00 F0 00 01 55 AA')
    ser.write(power)
    time.sleep(0.1)
    len_return_data = ser.inWaiting()

    if len_return_data:
        return_data = ser.read(len_return_data)
        #print(return_data)
        return_data = binascii.b2a_hex(return_data)
        #print(return_data[6:10])
        return_data = str(return_data[6:10])[2:6]
        return_data = int(return_data,16)
        #print(return_data)
    return return_data

#gps read
def gps_read():
    power = bytearray.fromhex('01 03 00 05 00 23 14 12')
    ser.write(power)
    time.sleep(0.1)
    len_return_data = ser.inWaiting()

    if len_return_data:
        return_data = ser.read(len_return_data)
       # print(return_data)
#time +8
        shijian = str(return_data).split(',')[1]
#N
        latit = str(return_data).split(',')[2]
#E
        longit = str(return_data).split(',')[4]
    return shijian,latit,longit


def main():
    args = parse_args()

    if args.power_up:
            up()

    if args.power_down:
            down()

    if args.power_read:
            power_read()

    if args.gps_read:
            gps_read()

'''    
if __name__ == '__main__':
    main()
'''

