import cv2
import sys
import time
import numpy as np
import multiprocessing as mp
from argparse import ArgumentParser
from settings import cam_addrs, img_shape,model_path,CLASSES
import hiai
from atlasutil import ai

t1,t2=0,0
def push_image(raw_q, cam_addr):
    global t1
    t1 = time.time()
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


def combine_images(queue_list,cam_addrs, img_shape):
    my_graph = ai.Graph(model_path)
    num_cameras = len(queue_list)
    while True:

        imgs = [cv2.resize(q.get(), img_shape) for q in queue_list]
        imgs_list = []
        for num in range(num_cameras):
            imgs_list.append(imgs[num])
            #ai/graph Inference(self, input_data)
        result_list = my_graph.Inference(imgs_list)
        if not result_list:
            print("get no result")
            return
        h, w = imgs[0].shape[0], imgs[1].shape[1]
        solution = (h, w)
        for num in range(num_cameras):
            detection_result_list = ai.SSDPostProcess(result_list[num], solution, 0.5, CLASSES)
            for result in detection_result_list:
                global t2
                t2 = time.time()
                print (result.result_text,cam_addrs[num],t2-t1)


def display_single_engine(cam_addrs,img_shape=(300, 300)):
    raw_queues = [mp.Queue(maxsize=4) for _ in cam_addrs]
    processes = []
    processes.append(mp.Process(target=combine_images, args=(raw_queues, cam_addrs, img_shape)))
    for raw_q,cam_addr in zip(raw_queues,cam_addrs):
        processes.append(mp.Process(target=push_image, args=(raw_q, cam_addr)))
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
    display_single_engine(cam_addrs[:args.num_cameras],img_shape)
