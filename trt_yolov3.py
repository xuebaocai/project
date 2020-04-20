"""trt_yolov3.py

This script demonstrates how to do real-time object detection with
TensorRT optimized YOLOv3 engine.
"""


import sys
import time
import argparse
import cv2
import pycuda.autoinit  # This is needed for initializing CUDA driver

from utils.yolov3_classes import get_cls_dict
from utils.yolov3 import TrtYOLOv3
from utils.visualization import BBoxVisualization
import threading

WINDOW_NAME = 'TrtYOLOv3Demo'
THREAD_RUNNING = False
IMG_HANDLE = None

def parse_args():
    """Parse input arguments."""
    desc = ('Capture and display live camera video, while doing '
            'real-time object detection with TensorRT optimized '
            'YOLOv3 model on Jetson Nano')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--model', type=str, default='yolov3-416',
                        choices=['yolov3-288', 'yolov3-416', 'yolov3-608',
                                 'yolov3-tiny-288', 'yolov3-tiny-416'])
    parser.add_argument('--name', dest='cam_name',default='admin')
    parser.add_argument('--password', dest='cam_password',default='182333')
    parser.add_argument('--ip', dest='cam_ip',
                        help='example 10.164.18.1',
                        default='10.14.18.1')

    args = parser.parse_args()
    return args

def open_cam_rtsp(name,password,ip):
    return cv2.VideoCapture('rtsp://{}:{}@{}:554'.format(name,password,ip))

def grab_img(cap):
    global THREAD_RUNNING
    global IMG_HANDLE
    while THREAD_RUNNING:
        _, IMG_HANDLE = cap.read()
        if IMG_HANDLE is None:
            #print('grab_img(): cap.read() returns None...')
            break
    THREAD_RUNNING = False

def loop_and_detect(trt_yolov3, conf_th, vis):
    """Continuously capture images from camera and do object detection.

    # Arguments
      cam: the camera instance (video source).
      trt_yolov3: the TRT YOLOv3 object detector instance.
      conf_th: confidence/score threshold for object detection.
      vis: for visualization.
    """
    global THREAD_RUNNING
    global IMG_HANDLE
    while THREAD_RUNNING:
        img = IMG_HANDLE
        if img is not None:
            boxes, confs, clss = trt_yolov3.detect(img, conf_th)
            img = vis.draw_bboxes(img, boxes, confs, clss)
            cv2.imshow(WINDOW_NAME, img)

        key = cv2.waitKey(1)
        if key == 27:  # ESC key: quit program
            break

def main():
    global THREAD_RUNNING
    args = parse_args()
    cls_dict = get_cls_dict('coco')
    yolo_dim = int(args.model.split('-')[-1])  # 416 or 608
    trt_yolov3 = TrtYOLOv3(args.model, (yolo_dim, yolo_dim))

    cap = open_cam_rtsp(args.cam_name,args.cam_password,args.cam_ip)
    if not cap.isOpened():
        sys.exit('Failed to open camera!')


    THREAD_RUNNING = True
    th = threading.Thread(target=grab_img, args=(cap,))
    th.start()

    vis = BBoxVisualization(cls_dict)
    loop_and_detect(trt_yolov3, conf_th=0.3, vis=vis)

    THREAD_RUNNING = False
    th.join()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
