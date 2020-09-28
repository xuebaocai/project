"""trt_main.py
This script demonstrates how to do real-time object detection with
TensorRT optimized Single-Shot Multibox Detector (SSD) engine.
"""

import sys
import time
import argparse
import cv2
import pycuda.autoinit
from utils.ssd_classes import get_cls_dict,DIGGER_CLASSES_LIST
from utils.ssd import TrtSSD
from utils.camera import add_camera_args, Camera
from utils.display import open_window, set_display, show_fps
from utils.visualization import BBoxVisualization
from control.camera_power import up
from mqtt.publish import Publish
import threading
import json


WINDOW_NAME = 'TrtSsdDemo'
INPUT_HW = (300, 300)
SUPPORTED_MODELS = [
    'ssd_mobilenet_v1_digger',
    'ssd_mobilenet_v2_digger',
]


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
    global Host
    print(Host)
    pub = Publish(host=Host)
    while True:

        if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
            break
        img = cam.read()
        if img is not None:
            boxes, confs, clss = trt_ssd.detect(img, conf_th)
            img, txt = vis.draw_bboxes(img, boxes, confs, clss)
            if str(txt).split(' ')[0] in DIGGER_CLASSES_LIST:
                # 鎶撴媿鐓х墖
                nowtime = int(time.time())
                if nowtime % 2 == 0:
                    img_signal = threading.Thread(target=pub.send_img,
                                                  args=('/zn/aicamera/img', img,))
                    img_signal.start()

                    msg_signal = threading.Thread(target=pub.send_msg,
                                                  args=('/zn/aicamera/alarm', txt,))
                    msg_signal.start()

            img = show_fps(img, fps)
            #cv2.imshow(WINDOW_NAME, img)
            toc = time.time()
            curr_fps = 1.0 / (toc - tic)
            # calculate an exponentially decaying average of fps number
            fps = curr_fps if fps == 0.0 else (fps * 0.95 + curr_fps * 0.05)
            tic = toc

        key = cv2.waitKey(1)
        if key == 27:  # ESC key: quit program
            break
        elif key == ord('F') or key == ord('f'):  # Toggle fullscreen
            full_scrn = not full_scrn
            set_display(WINDOW_NAME, full_scrn)


def main():
    args = parse_args()
    cam = Camera(args)
    json_path = '/home/mengjun/xianlu/tensorrt_demos/utils/config.json'
    with open(json_path,'r') as f:
       config = json.load(f)
    Host = config['Mqtt_pub']
    is_open = up()
    time.sleep(60)
    if is_open:
        cam.open()
        if not cam.is_opened:
            sys.exit('Failed to open camera!')

        cls_dict = get_cls_dict(args.model.split('_')[-1])
        trt_ssd = TrtSSD(args.model, INPUT_HW)

        cam.start()
        open_window(WINDOW_NAME, args.image_width, args.image_height,
                    'Camera TensorRT SSD Demo for Jetson Nano')
        vis = BBoxVisualization(cls_dict)
        loop_and_detect(cam, trt_ssd, conf_th=0.9, vis=vis)

        cam.stop()
        cam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
