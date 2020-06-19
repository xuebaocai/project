#2020.6.19 by mengjun V1.0
# opencv mutl ipcamera 

import cv2
import sys
import time
import numpy as np
import multiprocessing as mp
from settings import cam_addrs, img_shape
from argparse import ArgumentParser
import yolov3_tiny


def push_image(raw_q, cam_addr):
    cap = cv2.VideoCapture(cam_addr, cv2.CAP_FFMPEG)
    while True:
        is_opened, frame = cap.read()
        if is_opened:
            raw_q.put(frame)
        else:
            cap = cv2.VideoCapture(cam_addr, cv2.CAP_FFMPEG)
        if raw_q.qsize() > 1:
            # drop old images
            raw_q.get()
        else:
            # wait for stremaing
            time.sleep(0.01)


def predict(raw_q, pred_q):
    model = yolov3_tiny.general_yolov3()
    while True:
        
         raw_img = raw_q.get()
         result = model.predict(raw_img)

         label = model.vis_res(raw_img, result)
         pred_q.put(label)


def pop_result(pred_q,ip):

    while True:
        result = pred_q.get()
        print (result,ip)




def display(cam_addrs, ips):
    raw_queues = [mp.Queue(maxsize=2) for _ in cam_addrs]
    pred_queues = [mp.Queue(maxsize=4) for _ in cam_addrs]
    processes = []

    for raw_q, pred_q, cam_addr, ip in zip(raw_queues, pred_queues, cam_addrs, ips):
        processes.append(mp.Process(target=push_image, args=(raw_q, cam_addr)))
        processes.append(mp.Process(target=predict, args=(raw_q, pred_q)))
        processes.append(mp.Process(target=pop_result, args=(pred_q, ip)))

    [setattr(process, "daemon", True) for process in processes]
    [process.start() for process in processes]
    [process.join() for process in processes]

if __name__ == '__main__':
    mp.set_start_method(method='spawn')

    parser = ArgumentParser()
    parser.add_argument('--num_cameras', '-n', type=int,
                        help='number of cameras to process')
    args = parser.parse_args()
    args.num_cameras = len(cam_addrs) if args.num_cameras is None else args.num_cameras
    print(args.num_cameras)

    display(cam_addrs[:args.num_cameras], [ip for ip in cam_addrs])
