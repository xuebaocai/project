#2020.6.2
#v1.0 by mengjun
#camera power on and off ;read power

import sys
import time
import serial
import serial.rs485
import serial.tools.list_ports
import binascii




comport = '/dev/ttyUSB1'
baud = 9600


ser = serial.Serial(comport, baud)
print(ser.isOpen())

#power up
def up():
      up = bytearray.fromhex('01 10 00 E0 FF 00 55 AA')
      ser.write(up)
      time.sleep(0.1)

#power down
def down():
        down = bytearray.fromhex('01 10 00 E0 00 00 55 AA')
        ser.write(down)
        time.sleep(0.1)       

#power read
def read():
        power = bytearray.fromhex('01 03 00 F0 00 01 55 AA')
        ser.write(power)
        time.sleep(0.1)
        len_return_data = ser.inWaiting()
        #print('0x%x'%len_return_data)
        if len_return_data:
                return_data = ser.read(len_return_data)
                print(return_data)
                return_data = binascii.b2a_hex(return_data)
                #print(return_data[6:10])
                return_data = str(return_data[6:10])[2:6]
                return_data = int(return_data,16)
                print(return_data)
                

if __name__ == '__main__':
    read()

