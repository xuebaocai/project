"""trt_ssd_async.py

This is the 'async' version of trt_ssd.py implementation.  It creates
1 dedicated child thread for fetching camera input and do inferencing
with the TensorRT optimized SSD model/engine, while using the main
thread for drawing detection results and displaying video.  Ideally,
the 2 threads work in a pipeline fashion so overall throughput (FPS)
would be improved comparing to the non-async version.
"""


import sys
import time
import argparse
import threading

import cv2
import pycuda.driver as cuda

from utils.ssd_classes import get_cls_dict
from utils.ssd import TrtSSD
from utils.display import open_window, set_display, show_fps
from utils.visualization import BBoxVisualization


WINDOW_NAME = 'TrtSsdDemoAsync'
INPUT_HW = (300, 300)
SUPPORTED_MODELS = [
    'ssd_mobilenet_v1_coco',
    'ssd_mobilenet_v1_egohands',
    'ssd_mobilenet_v2_coco',
    'ssd_mobilenet_v2_egohands',
]

# These global variables are 'shared' between the main and child
# threads.  The child thread writes new frame and detection result
# into these variables, while the main thread reads from them.
s_img, s_boxes, s_confs, s_clss = None, None, None, None
THREAD_RUNNING = False
IMG_HANDLE = None

def parse_args():
    """Parse input arguments."""
    desc = ('Capture and display live camera video, while doing '
            'real-time object detection with TensorRT optimized '
            'SSD model on Jetson Nano')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--model', type=str, default='ssd_mobilenet_v2_coco',
                        choices=SUPPORTED_MODELS)
    parser.add_argument('--name', dest='cam_name',default='admin')
    parser.add_argument('--password', dest='cam_password',default='182333')
    parser.add_argument('--ip', dest='cam_ip',
                        help='example 10.164.18.1',
                        default='10.164.18.1:554')
    parser.add_argument('--width', dest='image_width',
                        help='image width [640]',
                        default=640, type=int)
    parser.add_argument('--height', dest='image_height',
                        help='image height [480]',
                        default=480, type=int)
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


class TrtThread(threading.Thread):
    """TrtThread

    This implements the child thread which continues to read images
    from cam (input) and to do TRT engine inferencing.  The child
    thread stores the input image and detection results into global
    variables and uses a condition varaiable to inform main thread.
    In other words, the TrtThread acts as the producer while the
    main thread is the consumer.
    """
    def __init__(self, condition,img, model, conf_th):
        """__init__

        # Arguments
            condition: the condition variable used to notify main
                       thread about new frame and detection result
            cam: the camera object for reading input image frames
            model: a string, specifying the TRT SSD model
            conf_th: confidence threshold for detection
        """
        threading.Thread.__init__(self)
        self.condition = condition
        self.img = img
        self.model = model
        self.conf_th = conf_th
        self.cuda_ctx = None  # to be created when run
        self.trt_ssd = None   # to be created when run
        self.running = False

    def run(self):
        """Run until 'running' flag is set to False by main thread.

        NOTE: CUDA context is created here, i.e. inside the thread
        which calls CUDA kernels.  In other words, creating CUDA
        context in __init__() doesn't work.
        """
        global s_img, s_boxes, s_confs, s_clss

        print('TrtThread: loading the TRT SSD engine...')
        self.cuda_ctx = cuda.Device(0).make_context()  # GPU 0
        self.trt_ssd = TrtSSD(self.model, INPUT_HW)
        print('TrtThread: start running...')
        self.running = True
        while self.running:
            boxes, confs, clss = self.trt_ssd.detect(self.img, self.conf_th)
            with self.condition:
                s_img, s_boxes, s_confs, s_clss = self.img, boxes, confs, clss
                self.condition.notify()
        del self.trt_ssd
        self.cuda_ctx.pop()
        del self.cuda_ctx
        print('TrtThread: stopped...')

    def stop(self):
        self.running = False
        self.join()


def loop_and_display(condition, vis):
    """Take detection results from the child thread and display.

    # Arguments
        condition: the condition variable for synchronization with
                   the child thread.
        vis: for visualization.
    """
    global s_img, s_boxes, s_confs, s_clss

    full_scrn = False
    fps = 0.0
    tic = time.time()
    while True:
        if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
            break
        with condition:
            # Wait for the next frame and detection result.  When
            # getting the signal from the child thread, save the
            # references to the frame and detection result for
            # display.
            condition.wait()
            img, boxes, confs, clss = s_img, s_boxes, s_confs, s_clss
        img = vis.draw_bboxes(img, boxes, confs, clss)
        img = show_fps(img, fps)
        cv2.imshow(WINDOW_NAME, img)
        toc = time.time()
        curr_fps = 1.0 / (toc - tic)
        # calculate an exponentially decaying average of fps number
        fps = curr_fps if fps == 0.0 else (fps*0.95 + curr_fps*0.05)
        tic = toc
        key = cv2.waitKey(1)
        if key == 27:  # ESC key: quit program
            break
        elif key == ord('F') or key == ord('f'):  # Toggle fullscreen
            full_scrn = not full_scrn
            set_display(WINDOW_NAME, full_scrn)


def main():
    global THREAD_RUNNING
    cuda.init()  # init pycuda driver

    args = parse_args()
    cap = open_cam_rtsp(args.cam_name, args.cam_password, args.cam_ip)
    if not cap.isOpened():
        sys.exit('Failed to open camera!')

    #抓取图像子进程
    THREAD_RUNNING = True
    th = threading.Thread(target=grab_img, args=(cap,))
    th.start()

    #目标识别
    cls_dict = get_cls_dict(args.model.split('_')[-1])

    open_window(WINDOW_NAME, args.image_width, args.image_height,
                'Camera TensorRT SSD Demo for Jetson Nano')
    vis = BBoxVisualization(cls_dict)
    condition = threading.Condition()
    global IMG_HANDLE
    trt_thread = TrtThread(condition,IMG_HANDLE, args.model, conf_th=0.3)
    trt_thread.start()  # start the child thread
    loop_and_display(condition, vis)
    trt_thread.stop()   # stop the child thread

    #关闭图像子进程
    THREAD_RUNNING = False
    th.join()
    cap.release()
    cv2.destroyAllWindows()



if __name__ == '__main__':
    main()
