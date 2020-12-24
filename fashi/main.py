"""trt_ssd.py

This script demonstrates how to do real-time object detection with
TensorRT optimized Single-Shot Multibox Detector (SSD) engine.
"""


import time
import argparse
import os
import cv2
import json
import pycuda.autoinit  # This is needed for initializing CUDA driver
import numpy as np
from utils.ssd_classes import get_cls_dict
from utils.ssd import TrtSSD
from utils.camera import add_camera_args, Camera
from utils.display import open_window, set_display, show_fps
from utils.visualization import BBoxVisualization
from utils.data_sys import DataSynchronization

WINDOW_NAME = 'TrtSsdDemo'
INPUT_HW = (300, 300)
SUPPORTED_MODELS = [
    'ssd_mobilenet_v1_digger',
]


def parse_args():
    """Parse input arguments."""
    desc = ('Capture and display live camera video, while doing '
            'real-time object detection with TensorRT optimized '
            'SSD model on Jetson Nano')
    parser = argparse.ArgumentParser(description=desc)
    parser = add_camera_args(parser)
    parser.add_argument('-m', '--model', type=str,
                        default='ssd_mobilenet_v1_digger',
                        choices=SUPPORTED_MODELS)
    args = parser.parse_args()
    return args

def main(config):
    args = parse_args()

    cls_dict = get_cls_dict(args.model.split('_')[-1])
    trt_ssd = TrtSSD(args.model, INPUT_HW)
    while True:
      img_list = []
      if len(config['Channel']) == 1:
        print('1')
        cap = cv2.VideoCapture('digger1.mp4', cv2.CAP_FFMPEG)
        frame,img = cap.read()
        if img is not None:
          img_list.append([img])
        else:
          continue
        
        
      if len(config['Channel']) == 2:
        print('2')
        cap1 = cv2.VideoCapture('digger1.mp4', cv2.CAP_FFMPEG)
        cap2 = cv2.VideoCapture('rtsp://admin:admin12345@10.151.96.197:554/Streaming/Channels/101', cv2.CAP_FFMPEG)
        frame,img1 = cap1.read()
        frame,img2 = cap2.read()
        if img1 is not None and img2 is not None:
          img_list.append([img1,img2])
        else:
          continue
      result = trt_ssd.detect(img_list[0], conf_th=0.5)
      print(img_list[0][0].shape)
      print(img_list[0][1].shape)
      DataSynchronization(result,img_list,args.model,'boundary_intrude',None,config['Camera_ip'],config['Channel'],config['Mqtt_pub'],config['Polygon'])
      
    cap1.release()
    cap2.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    pwd = os.getcwd()
    json_path = pwd+'/utils/config.json'
    with open(json_path,'r') as f:
       config = json.load(f)
    main(config)
