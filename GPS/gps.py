#2020.3.26
import serial
import pynmea2


def open_gps(comport = '/dev/ttyUSB0',band = 9600,send=False):
    '''
    :param comport:
    :param band:
    :param timeout:
    :return: record.lat,record.lon
    '''
    ser = serial.Serial(comport,band)
    if send == True:
       if ser.isOpen():
            recv = ser.readline().decode()
            if recv.startswith('$'):
                record = pynmea2.parse(recv)
                if recv.startswith('$GPRMC'):
                    return (record.lat,record.lon)
           

