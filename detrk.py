import os
import argparse
import cv2
import time
import numpy as np
import pycuda.autoinit
from sort import Sort
from utils.ssd import TrtSSD
from utils.camera import add_camera_args, Camera
from utils.display import open_window, set_display, show_fps

def parse_args():
    '''parse args'''
    parser = argparse.ArgumentParser()

    parser = add_camera_args(parser)
    parser.add_argument('--model', type=str, default='ssd_mobilenet_v1_digger')
    parser.add_argument('--image_resize', default=300, type=int)
    parser.add_argument('--det_conf_thresh', default=0.8, type=float)
    parser.add_argument('--seq_dir', default="sequence/")
    parser.add_argument('--sort_max_age', default=5, type=int)
    parser.add_argument('--sort_min_hit', default=3, type=int)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    trt_ssd = TrtSSD(args.model, (args.image_resize, args.image_resize))

    mot_tracker = Sort(args.sort_max_age, args.sort_min_hit)
    video = '/home/mengjun/xianlu/data/digger.mp4'
    cap = cv2.VideoCapture(video)
    colours = np.random.rand(32, 3) * 255
    fps = 0.0
    tic = time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        boxes, confs, clss = trt_ssd.detect(frame, args.det_conf_thresh)
        #print(boxes, confs, clss)
        if len(boxes) != 0:
            result = []
            for bb, cf, cl in zip(boxes, confs, clss):
                 result.append([bb[0], bb[1], bb[2], bb[3], cl])
            result = np.array(result,dtype=object)
            #print('result:',result)
            height = frame.shape[0]
            width = frame.shape[1]

            if len(clss) == 0:
                continue
            else:
                det = result[:, 0:5]
                print('det:',det)
                #det[:, 0] = det[:, 0] * width
                #det[:, 1] = det[:, 1] * height
                #det[:, 2] = det[:, 2] * width
                #det[:, 3] = det[:, 3] * height
                #print('det1',det)
                trackers = mot_tracker.update(det)
                frame = show_fps(frame, fps)
                toc = time.time()
                curr_fps = 1.0 / (toc - tic)
                # calculate an exponentially decaying average of fps number
                fps = curr_fps if fps == 0.0 else (fps * 0.95 + curr_fps * 0.05)
                tic = toc
                
                for d in trackers:
                    xmin = int(d[0])
                    ymin = int(d[1])
                    xmax = int(d[2])
                    ymax = int(d[3])
                    label = int(d[4])
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
                    cv2.imshow("dst", frame)
                    cv2.waitKey(1)





