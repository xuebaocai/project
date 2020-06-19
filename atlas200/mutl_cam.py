#2020.6.19 by mengjun V1.0
# opencv mutl ipcamera 

import cv2
import sys
import time
import numpy as np
import multiprocessing as mp
import yolov3_tiny
from settings import cam_addrs, img_shape
from argparse import ArgumentParser

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
    while True:
        raw_img = raw_q.get()
        model = yolov3_tiny.general_yolov3()
        result = model.predict(raw_img)
        pred_img = model.vis_res(raw_img,result)
        pred_q.put(pred_img)


def pop_image(pred_q, window_name, img_shape):
    cv2.namedWindow(window_name, flags=cv2.WINDOW_FREERATIO)
    while True:
        frame = pred_q.get()
        frame = cv2.resize(frame, img_shape)
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)

def display(cam_addrs, window_names, img_shape=(300, 300)):
    raw_queues = [mp.Queue(maxsize=2) for _ in cam_addrs]
    pred_queues = [mp.Queue(maxsize=4) for _ in cam_addrs]
    processes = []

    for raw_q, pred_q, cam_addr, window_name in zip(raw_queues, pred_queues, cam_addrs, window_names):
        processes.append(mp.Process(target=push_image, args=(raw_q, cam_addr)))
        processes.append(mp.Process(target=predict, args=(raw_q, pred_q)))
        processes.append(mp.Process(target=pop_image, args=(pred_q, window_name, img_shape)))

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
    
    display(cam_addrs[:args.num_cameras], ['camera' for _ in cam_addrs], img_shape)
