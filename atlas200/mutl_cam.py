#2020.6.23 by mengjun V1.1
# opencv mutl ipcamera 


import cv2
import sys
import time
import numpy as np
import multiprocessing as mp
from settings import cam_addrs, img_shape,model_path,CLASSES
from argparse import ArgumentParser
import hiai
from atlasutil import ai

model_path = model_path
CLASSES = CLASSES


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
    my_graph = ai.Graph(model_path)
    while True:
        raw_img = raw_q.get()
        raw_img = cv2.resize(raw_img,img_shape)
        result_list = my_graph.Inference(raw_img)
        if not result_list:
            print("get no result")
            return
        h, w = raw_img.shape[0], raw_img.shape[1]
        solution = (h, w)
        detection_result_list = ai.SSDPostProcess(result_list[0], solution, 0.5, CLASSES)
        for result in detection_result_list:
            pred_q.put(result.result_text)



def pop_result(pred_q,ip):
    while True:
        if not pred_q.empty():
            result = pred_q.get()
            print (result,ip)


def display(cam_addrs, ips):
    raw_queues = [mp.Queue(maxsize=16) for _ in cam_addrs]
    pred_queues = [mp.Queue(maxsize=32) for _ in cam_addrs]
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



