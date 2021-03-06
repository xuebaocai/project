# !/usr/bin/env python
# -*- coding:utf-8 -*-  



import ctypes
from ctypes import *
import os
import sys
import numpy as np
from multiprocessing import Process, Array,Value
from datetime import datetime


CAMERA_IMAGE_FORMAT_YUV420_SP = 1
CAMERA_IMAGE_FORMAT_JPEG = 2
CAMERA_IMAGE_FORMAT_RGBU888 = 3

CAMERA_OK = 0
CAMERA_ERROR = 1

CAMERA_CLOSED = 0
CAMERA_OPENED = 1

class CameraImageBuf(Structure):
    _fields_ = [
        ('size', c_uint),
        ('data', POINTER(c_ubyte))
    ]

class CameraConfigCtypes(Structure):
    _fields_ = [
        ('id',     c_int),
        ('fps',    c_int),
        ('width',  c_int),
        ('height', c_int),
        ('format', c_int)
    ]

class CameraConfig():
    def __init__(self, id, fps, width, height, format):
        self.id = id
        self.fps = fps
        self.width = width
        self.height = height
        self.format = format


class Camera():
    lib = ctypes.CDLL(os.path.dirname(os.path.abspath(__file__)) + '/libcamera.so')

    def __init__(self, id, fps = 5, width = 1280, height = 720, format = CAMERA_IMAGE_FORMAT_YUV420_SP):
        self.id = id
        self.config = CameraConfig(id, fps, width, height, format)
        if format == CAMERA_IMAGE_FORMAT_YUV420_SP:
            self.size = int(width * height * 3 / 2)
        else:
            self.size = width * height * 3
        self.image_buf = CameraImageBuf()
        self.image_buf.size = self.size
        self.image_buf.data = (c_ubyte * self.image_buf.size)()
        self.status = CAMERA_CLOSED
        self.Open()

    def Open(self):
        camera_config = CameraConfigCtypes()
        camera_config.id     = self.id
        camera_config.fps    = self.config.fps
        camera_config.width  = self.config.width
        camera_config.height = self.config.height
        camera_config.format = self.config.format
        ret = Camera.lib.Open(byref(camera_config))
        if (ret != CAMERA_OK):
            print("Open camera %d failed"%(self.id))
            return CAMERA_ERROR
        self.status = CAMERA_OPENED

        return CAMERA_OK

    def IsOpened(self):
        return (self.status == CAMERA_OPENED)

    def Read(self):
        self.image_buf.size = self.size
        ret = Camera.lib.Read(self.id, byref(self.image_buf))
        if (ret != CAMERA_OK):
            print("Read camera %d failed"%(self.id))
            return CAMERA_ERROR
        image_array = np.frombuffer((ctypes.c_ubyte * self.image_buf.size).from_address(ctypes.addressof(self.image_buf.data.contents)), dtype=np.uint8)
        return image_array

    def Close(self):
        Camera.lib.Close(self.id)
        self.status = CAMERA_CLOSED

    def __del__(self):
        if self.IsOpened():
            self.Close()
            print("camera %d closed"%(self.id))


if __name__ == "__main__":
    cap = Camera(0)
    cap.Open()
    start = datetime.now()
    cap.Read()
    end = datetime.now() - start
    print("Read total exhaust ", end.total_seconds())



