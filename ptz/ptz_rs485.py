"""
===================================
Antenna Tracker PTZ controller v2.0
Author: Oleksii Savchenko
Date: 01.2019
Update: 07.2019
Realese -
===================================
Pelco-D protocol
LEFT  - FF 01 00 04 3F 00 44
RIGHT - FF 01 00 02 3F 00 42
UP    - FF 01 00 08 00 27 30
DOWN  - FF 01 00 10 00 27 38
STOP  - FF 01 00 00 00 00 01
ZOOM IN - FF 01 00 20 00 00 21
ZOOM OUT - FF 01 00 40 00 00 41
===========================================
Make EXE file from project:
pyinstaller --onefile ptz_control_rs485.py
===========================================
"""
import cv2
import tkinter
from tkinter import Tk, Canvas
from PIL import Image, ImageTk
from pynput.keyboard import Key
import sys
import time
import serial
import serial.rs485
import serial.tools.list_ports

# ======= Change COMPORT =====================
ports = serial.tools.list_ports.comports()

for port, desc, hwid in sorted(ports):
    print ('[{}]: '.format(port, desc, hwid))
# ============================================

# Input true comport ===========================
comport = 'com2'
baud = 2400
# ==============================================
# ==============================================
try:
    ser = serial.Serial(comport, baud)

    ser.rs485_mode = serial.rs485.RS485Settings(rts_level_for_tx=True, rts_level_for_rx=False, loopback=False,
                                                delay_before_tx=None, delay_before_rx=None)
    print("Port open: " + str(comport))

except serial.serialutil.SerialException:
    print ("RS-485 not connected..." '\n')
    print ("Please connect RS-485 module ")
    exit()


# =====================================================================
# Some functions for control
# =====================================================================

def up():
    up = bytearray.fromhex('FF 01 00 08 00 27 30')
    #print ('UP')
    #print ('FF 01 00 08 00 27 30')
    ser.write(up)
    return up


def down():
    down = bytearray.fromhex('FF 01 00 10 00 27 38')
    #print ('DOWN')
    #print ('FF 01 00 10 00 27 38')
    ser.write(down)
    return down


def right():
    right = bytearray.fromhex('FF 01 00 02 3F 00 42')
    #print ('RIGHT')
    #print ('FF 01 00 02 20 00 23')
    ser.write(right)
    return right


def left():
    left = bytearray.fromhex('FF 01 00 04 3F 00 44')
    #print ('LEFT')
    #print ('FF 01 00 04 3F 00 44')
    ser.write(left)
    return left


def stop():
    stop = bytearray.fromhex('FF 01 00 00 00 00 01')
    #print ('STOP')
    #print ('FF 01 00 00 00 00 01')
    ser.write(stop)
    return stop


def zoom_in():
    stop = bytearray.fromhex('FF 01 00 00 00 00 01')
    zoom_in = bytearray.fromhex('FF 01 00 20 00 00 21')
    ser.write(zoom_in)
    #print ('zoom_in')
    return zoom_in


def zoom_out():
    stop = bytearray.fromhex('FF 01 00 00 00 00 01')
    zoom_out = bytearray.fromhex('FF 01 00 40 00 00 41')
    ser.write(zoom_out)
    #print ('zoom_out')
    return zoom_out


def pan_parking():
    stop = bytearray.fromhex('FF 01 00 00 00 00 01')
    pan_parking = bytearray.fromhex('FF 01 00 4B 8C A0 78')
    #print ('FF 01 00 4B 8C A0 78')
    ser.write(pan_parking)
    #print('pan_parking_0')
    return pan_parking


def pan_angle():
    stop = bytearray.fromhex('FF 01 00 00 00 00 01')
    pan_angle = bytearray.fromhex('FF 01 00 4B 23 28 97')
    #print ('FF 01 00 4B 23 28 97')
    ser.write(pan_angle)
    #print('pan_angle_90')
    return pan_angle

def look_angle():
    look_angle = bytearray.fromhex('FF 01 00 53 00 00 54')
    #print ('FF 01 00 53 00 00 54')
    ser.write(look_angle)
    return look_angle


def close_window():
    root.destroy()


# ============
# MAIN WINDOW
# ============
# ============================================
# Keyboard key : Left, Right, Up, Down, Space
# ============================================
def leftKey(event):
    print("Left key pressed...")
    left_step = left()
    ser.write(left_step)
    time.sleep(0.5)
    lock = stop()
    ser.write(lock)


def rightKey(event):
    print("Right key pressed...")
    right_step = right()
    ser.write(right_step)
    time.sleep(0.5)
    lock = stop()
    ser.write(lock)


def upKey(event):
    print("Up key pressed...")
    up_step = up()
    ser.write(up_step)
    time.sleep(0.5)
    lock = stop()
    ser.write(lock)


def downKey(event):
    print("Up key pressed...")
    down_step = down()
    ser.write(down_step)
    time.sleep(0.5)
    lock = stop()
    ser.write(lock)


def spaceKey(event):
    stop_stop = stop()
    ser.write(stop_stop)


# ======= End keyboard =============

root = Tk()
root.title('AntennaTracker v2.0')
root.geometry('600x160')
root.configure(background='black')

root.bind('<Left>', leftKey)
root.bind('<Right>', rightKey)
root.bind('<Up>', upKey)
root.bind('<Down>', downKey)
root.bind('<space>', spaceKey)
# ==================
# Create a canvas
# =================
canvas_wight = 110
canvas_height = 110
canvas = Canvas(root, width=canvas_wight, height=canvas_height, background='black')
canvas.place(x=185, y=10, width=110)

# ====================
# Load the image file
# ====================
logo = Image.open('E:/project/helmet/PTZ/ptz_logo.png')
# Put the image into a canvas compatible class, and stick in an
# arbitrary variable to the garbage collector doesn't destroy it
canvas.image = ImageTk.PhotoImage(logo)
# Add the image to the canvas, and set the anchor to the root left / north west corner
canvas.create_image(0, 0, image=canvas.image, anchor='nw')

# ========
# BUTTONS
# ========
# UP

button = tkinter.Button(root, text="UP", fg="white", bg='black', command=up).place(x=65, y=35, width=55)
# DOWN
button = tkinter.Button(root, text="DOWN", fg="white", bg='black', command=down).place(x=65, y=65, width=55)
# RIGHT
button = tkinter.Button(root, text="RIGHT", fg="white", bg='black', command=right).place(x=125, y=100, width=55)
# LEFT
button = tkinter.Button(root, text="LEFT", fg="white", bg='black', command=left).place(x=5, y=100, width=55)
# !!! STOP !!!
button = tkinter.Button(root, text="STOP", fg="red", bg='black', command=stop).place(x=65, y=100, width=55)
# EXIT
button = tkinter.Button(root, text="EXIT", fg="black", command=close_window)
button.place(x=530, y=10, width=55)

# TEST!!!
#button = Tkinter.Button(root, text="TEST", fg="white", bg='black', width=15, command=stop)
#button.place(x=300, y=70, width=55)
# PRESET01!!!
button = tkinter.Button(root, text="Pan360", fg="white", bg='grey', width=15, command=pan_parking)
button.place(x=390, y=70, width=65)
# PRESET02!!!
button = tkinter.Button(root, text="Pan90", fg="white", bg='gray', width=15, command=pan_angle)
button.place(x=390, y=100, width=65)
# PRESET03!!!
button = tkinter.Button(root, text="ZoomIN", fg="white", bg='gray', width=15, command=zoom_in)
button.place(x=320, y=100, width=65)
# PRESET04!!!
button = tkinter.Button(root, text="ZoomOUT", fg="white", bg='gray', width=15, command=zoom_out)
button.place(x=320, y=70, width=65)
# PRESET05!!!
button = tkinter.Button(root, text="Titl Angle", fg="white", bg='black', width=15, command=look_angle)
button.place(x=460, y=100, width=65)
# PRESET06!!!
button = tkinter.Button(root, text="PRESET", fg="white", bg='black', width=15, command=stop)
button.place(x=460, y=70, width=65)
# PRESET07!!!
button = tkinter.Button(root, text="PRESET", fg="white", bg='black', width=15, command=stop)
button.place(x=530, y=70, width=65)
# PRESET06!!!
button = tkinter.Button(root, text="PRESET", fg="white", bg='black', width=15, command=stop)
button.place(x=530, y=100, width=65)
# ==================
# End of programm
# ==================
root.mainloop()
ser.close()