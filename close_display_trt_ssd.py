"""trt_ssd.py

This script demonstrates how to do real-time object detection with
TensorRT optimized Single-Shot Multibox Detector (SSD) engine.
ssd_mobilenet_v1_digger:20FPS
ssd_mobilenet_v1_digger:19FPS
"""


import sys
import time
import argparse

import cv2
import pycuda.autoinit  # This is needed for initializing CUDA driver

from utils.ssd_classes import get_cls_dict
from utils.ssd import TrtSSD
from utils.camera import add_camera_args, Camera
from utils.display import open_window, set_display, show_fps
from utils.visualization import BBoxVisualization


WINDOW_NAME = 'TrtSsdDemo'
INPUT_HW = (300, 300)
SUPPORTED_MODELS = [
    'ssd_mobilenet_v1_coco',
    'ssd_mobilenet_v2_coco',
    'ssd_mobilenet_v1_digger',
    'ssd_mobilenet_v2_digger',  
]

label_map = {'1':'person','2':'hat','3':'digger','4':'truck'}


def parse_args():
    """Parse input arguments."""
    desc = ('Capture and display live camera video, while doing '
            'real-time object detection with TensorRT optimized '
            'SSD model on Jetson Nano')
    parser = argparse.ArgumentParser(description=desc)
    parser = add_camera_args(parser)
    parser.add_argument('--model', type=str, default='ssd_mobilenet_v1_digger',
                        choices=SUPPORTED_MODELS)
    args = parser.parse_args()
    return args


def loop_and_detect(cam, trt_ssd, conf_th, vis):
    """Continuously capture images from camera and do object detection.

    # Arguments
      cam: the camera instance (video source).
      trt_ssd: the TRT SSD object detector instance.
      conf_th: confidence/score threshold for object detection.
      vis: for visualization.
    """
    full_scrn = False
    fps = 0.0
    tic = time.time()
    label_cf = {}
    while True:
        img = cam.read()
        if img is not None:
            boxes, confs, clss = trt_ssd.detect(img, conf_th)
            img = vis.draw_bboxes(img, boxes, confs, clss)

            toc = time.time()
            curr_fps = 1.0 / (toc - tic)
            
            
            for num,cf in zip(clss,confs):
                 label = label_map['{}'.format(num)]
                 cf = float('%.2f'%cf)
                 label_cf['{}'.format(label)] = cf
            print(label_cf,curr_fps)
            
            fps = curr_fps if fps == 0.0 else (fps*0.9 + curr_fps*0.1)
            tic = toc
            label_cf = {}


def main():
    args = parse_args()
    cam = Camera(args)
    cam.open()
    if not cam.is_opened:
        sys.exit('Failed to open camera!')

    cls_dict = get_cls_dict(args.model.split('_')[-1])
    trt_ssd = TrtSSD(args.model, INPUT_HW)

    cam.start()
    #open_window(WINDOW_NAME, args.image_width, args.image_height,'Camera TensorRT SSD Demo for Jetson Nano')
    vis = BBoxVisualization(cls_dict)
    loop_and_detect(cam, trt_ssd, conf_th=0.1, vis=vis)

    cam.stop()
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
