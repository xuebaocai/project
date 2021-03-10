import sys
import time
import argparse
import cv2
import pycuda.autoinit
import numpy as np
from utils.ssd_classes import get_cls_dict, DIGGER_CLASSES_LIST
from utils.ssd import TrtSSD
from utils.camera import add_camera_args, Camera
from utils.display import open_window, set_display, show_fps
from utils.visualization import BBoxVisualization
from control.camera_power import up, down
from mqtt.publish import Publish
import json

WINDOW_NAME = 'TrtSsdDemo'
INPUT_HW = (300, 300)
SUPPORTED_MODELS = [
    'ssd_mobilenet_v1_coco',
    'ssd_mobilenet_v2_coco',
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

class Point():
    def __init__(self):
        self.x = 0
        self.y = 0


def ray_casting(p, poly):
    if len(poly) < 3:
        return False
    flag = False
    l = len(poly)
    j = l - 1
    for i in range(0, l):
        sx = poly[i][0]
        sy = poly[i][1]
        tx = poly[j][0]
        ty = poly[j][1]
        if (sx == p.x and sy == p.y) or (tx == p.x and ty == p.y):
            return True
        if (sy < p.y <= ty) or (sy >= p.y > ty):
            x = sx + (p.y - sy) * (tx - sx) / (ty - sy)
            if x == p.x:
                return True
            if x > p.x:
                flag = not flag
        j = i
        i += 1
    return flag

def is_working(work_time):
    if int(work_time[0][0]) <= int(time.strftime("%H%M%S")) <= int(work_time[1][0]):
        return True
    else:
        return False

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
    pub = Publish(host=Host)
    while is_working(Work_time):
        # if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
        #    break
        img = cam.read()
        if img is not None:
            boxes, confs, clss = trt_ssd.detect(img, conf_th)
            if config['Is_Polygon'] == '1':
                print('Is_Polygon')
                pt = Point()
                for bb in boxes:
                    pt.x = int((bb[0] + bb[2]) * 0.5)
                    pt.y = int(0.3 * bb[1] + 0.7 * bb[3])
                flag = ray_casting(pt, config['Polygon'])
                if flag == True:
                    # cv2.circle(img, (pt.x, pt.y), 20,(255,0,0), 0)
                    img, txt = vis.draw_bboxes(img, boxes, confs, clss)

                    if str(txt).split(' ')[0] in DIGGER_CLASSES_LIST:
                        if str(txt).split(' ')[0] in DIGGER_CLASSES_LIST:
                            pub.send_img('/zn/aicamera/{}/{}/img'.format(config['zone'], config['channel']), img)
                            pub.send_msg('/zn/aicamera/{}/{}/alarm'.format(config['zone'], config['channel']),
                                         'type-{},time-{}'.format(txt, time.ctime()))

                        print('flag:', flag, 'confs:', confs, 'clss:', clss, 'fps:', fps)

            else :
                print('Not_Polygon')
                img, txt = vis.draw_bboxes(img, boxes, confs, clss)
                if str(txt).split(' ')[0] in DIGGER_CLASSES_LIST:
                    pub.send_img('/zn/aicamera/{}/{}/img'.format(config['zone'], config['channel']),img)
                    pub.send_msg('/zn/aicamera/{}/{}/alarm'.format(config['zone'], config['channel']),'type-{},time-{}'.format(txt, time.ctime()))

                    print('confs:', confs, 'clss:', clss, 'fps:', fps)


        key = cv2.waitKey(1)
        if key == 27:  # ESC key: quit program
            break



def main():
    args = parse_args()
    cam = Camera(args)
    cam.open()
    if not cam.is_opened:
        sys.exit('Failed to open camera!')

    cls_dict = get_cls_dict(args.model.split('_')[-1])
    trt_ssd = TrtSSD(args.model, INPUT_HW)

    cam.start()
    '''
    open_window(WINDOW_NAME, args.image_width, args.image_height,
                'Camera TensorRT SSD Demo for Jetson Nano')
    '''
    vis = BBoxVisualization(cls_dict)
    loop_and_detect(cam, trt_ssd, conf_th=0.5, vis=vis)

    cam.stop()
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    json_path = '/home/mengjun/xianlu/tensorrt_demos/utils/config.json'
    with open(json_path, 'r') as f:
        config = json.load(f)
    Host = config['Mqtt_pub']
    Work_time = config['Work_time']
    while True:
        if is_working(Work_time):
           main()
           print('on')
           time.sleep(10)

        else:
            print('down')
            down()
            time.sleep(100)
