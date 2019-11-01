import serial
import pynmea2 
ser = serial.Serial()
comport = '/dev/ttyUSB0'
baud = 9600
ser = serial.Serial(comport, baud,timeout=0.5)
while ser.isOpen():
	recv = ser.readline().decode()
	if recv.startswith('$'):
		record = pynmea2.parse(recv)
		if recv.startswith('$GPRMC'):
			return(record.lat,record.lon)

           

