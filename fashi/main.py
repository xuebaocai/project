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
from utils.data_sys import Data_sys
from utils.publish import Publish

WINDOW_NAME = 'TrtSsdDemo'
INPUT_HW = (300, 300)
SUPPORTED_MODELS = [
    'ssd_mobilenet_v1_coco',
]


def parse_args():
    """Parse input arguments."""
    desc = ('Capture and display live camera video, while doing '
            'real-time object detection with TensorRT optimized '
            'SSD model on Jetson Nano')
    parser = argparse.ArgumentParser(description=desc)
    parser = add_camera_args(parser)
    parser.add_argument('-m', '--model', type=str,
                        default='ssd_mobilenet_v1_coco',
                        choices=SUPPORTED_MODELS)
    args = parser.parse_args()
    return args

def main(config):
    args = parse_args()
    data_sys = Data_sys()
    pub = Publish(host=config['Mqtt_pub'])

    cls_dict = get_cls_dict(args.model.split('_')[-1])
    trt_ssd = TrtSSD(args.model, INPUT_HW)

    img_list = []

    # video
    cap = cv2.VideoCapture('xiasha.avi')
    i = 0
    while cap.isOpened():
        frame, img = cap.read()
        if img is not None:

            img_list.append([img])
            result = trt_ssd.detect(img_list[0], conf_th=0.3)
            # print(result)
            data_sys.dataSynchronization(result, img_list, args.model, ['boundary_intrude', None], config['Zone'],
                                         config['Channel'][0], config['device_id'], pub, config['Polygon'])
            img_list = []
            i = i + 1
            print(i)
        else:
            msg = json.dumps({
                "nvr_id": config['Zone'],
                "device_id": config['device_id'],
                "channel_id": config['Channel'][0]})
            pub.send_msg(topic= "zs/ai_spxwfx/rtsp/" + config['Zone'] + "/" + config['Channel'][0], msg=msg, Zone=config['Zone'], device_id=config['device_id'])
            
            
    '''
    #img
    img = cv2.imread('zhannei_9.jpg')
    img_list.append([img])
    result = trt_ssd.detect(img_list[0], conf_th=0.3)
    #print(result)
    DataSynchronization(result,img_list,args.model,['boundary_intrude',None],config['Zone'],config['Channel'][0],config['Mqtt_pub'],config['Polygon'],history_data,start_time)
    
    #rstp
    if len(config['Channel']) == 1:
      print('1')
      #cap = cv2.VideoCapture('rtsp://admin:admin12345@{}:554/Streaming/Channels/{}01'.format(config['Camera_ip'],config['Channel'][0]))
      cap = cv2.VideoCapture('xiasha.avi')
      while cap.isOpened():
        frame,img = cap.read()
        if img is not None:
          print(img.shape)
          img_list.append([img])
          result = trt_ssd.detect(img_list[0], conf_th=0.3)
          if len(result[0][0]) != 0 :
            DataSynchronization(result,img_list,args.model,['boundary_intrude',None],config['Zone'],config['Channel'],config['Mqtt_pub'],config['Polygon'])
        else:
          continue
        
        
    if len(config['Channel']) == 2:
      print('2')
      cap1 = cv2.VideoCapture('rtsp://admin:admin12345@{}:554/Streaming/Channels/{}01'.format(config['Camera_ip'],config['Channel'][0]))
      cap2 = cv2.VideoCapture('rtsp://admin:admin12345@{}:554/Streaming/Channels/{}01'.format(config['Camera_ip'],config['Channel'][1]))
      while cap1.isOpened() and cap2.isOpened():
        frame,img1 = cap1.read()
        frame,img2 = cap2.read()
        if img1 is not None and img2 is not None:
          print(img1.shape,img2.shape)
          img_list.append([img1,img2])
          result = trt_ssd.detect(img_list[0], conf_th=0.3)
          print(result)
          if len(result[0][0]) !=0 or len(result[1][0]) != 0:
            DataSynchronization(result,img_list,args.model,['boundary_intrude',None],config['Camera_ip'],config['Channel'],config['Mqtt_pub'],config['Polygon'])
        else:
          continue
    
    if len(config['Channel']) == 1:
      cap.release()
    else:
      cap1.release()
      cap2.release()
    cv2.destroyAllWindows()
    '''

if __name__ == '__main__':
    pwd = os.getcwd()
    json_path = pwd+'/utils/config.json'
    with open(json_path,'r') as f:
       config = json.load(f)
    main(config)

