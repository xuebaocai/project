#11.01 
#no show just save image

import os
import sys
import time
import argparse
import threading
import numpy as np
import cv2
from google.protobuf import text_format
import send_email

CAFFE_ROOT = '/home/junmeng/project/ssd-caffe/'
sys.path.insert(0, CAFFE_ROOT + 'python')
import caffe
from caffe.proto import caffe_pb2


DEFAULT_PROTOTXT = CAFFE_ROOT + 'models/googlenet_fc/coco/SSD_300x300/deploy.prototxt'
DEFAULT_MODEL    = CAFFE_ROOT + 'models/googlenet_fc/coco/SSD_300x300/deploy.caffemodel'
DEFAULT_LABELMAP = CAFFE_ROOT + 'data/coco/labelmap_coco.prototxt'

PIXEL_MEANS = np.array([[[104.0, 117.0, 123.0]]], dtype=np.float32)

#camera ip
uri = 'rtsp://admin:182333@10.164.18.251:554'
conf_th=0.3


#intrusion roi
roi_x1 = 50
roi_y1 = 50
roi_x2 = 1000
roi_y2 = 600


#saved_img_path
saved_img_path = '/home/junmeng/helmet/saved_img/'




def open_cam_rtsp(uri):
    return cv2.VideoCapture(uri)

def preprocess(src):
    '''Preprocess the input image for SSD
    '''
    img = cv2.resize(src, (300, 300))
    img = img.astype(np.float32) - PIXEL_MEANS
    return img


def postprocess(img, out):
    '''Postprocess the ouput of the SSD object detector
    '''
    h, w, c = img.shape
    box = out['detection_out'][0,0,:,3:7] * np.array([w, h, w, h])

    cls = out['detection_out'][0,0,:,1]
    conf = out['detection_out'][0,0,:,2]
    return (box.astype(np.int32), conf, cls)


def detect(origimg, net):
    img = preprocess(origimg)
    img = img.transpose((2, 0, 1))

    tic = time.time()
    net.blobs['data'].data[...] = img
    out = net.forward()
    dt = time.time() - tic
    box, conf, cls = postprocess(origimg, out)
    return (box, conf, cls,dt)


def show_bounding_boxes(img, box, conf, cls, cls_dict, conf_th):
    for bb, cf, cl in zip(box, conf, cls):
        cl = int(cl)
        # Only keep non-background bounding boxes with confidence value
        # greater than threshold
        if cl == 0 or cf < conf_th:
            continue

        x_min, y_min, x_max, y_max = bb[0], bb[1], bb[2], bb[3]
	#if intrusion 
        if (x_min > roi_x1) & (y_min > roi_y1) & (x_max < roi_x2) & (y_max < roi_y2):        
            cv2.rectangle(img, (x_min,y_min), (x_max,y_max), BBOX_COLOR, 2)
            txt_loc = (max(x_min, 5), max(y_min-3, 20))
            cls_name = cls_dict.get(cl, 'CLASS{}'.format(cl))
            txt = '{} {:.2f}'.format(cls_name, cf)
            cv2.putText(img, txt, txt_loc, cv2.FONT_HERSHEY_DUPLEX, 0.8, BBOX_COLOR, 1)     
            cv2.imwrite(saved_img_path+str(time.ctime(time.time())[4:19].replace(':','_')+'.jpg',img)
	

def read_cam_and_detect(img, net, cls_dict, conf_th):
    box, conf, cls,dt = detect(img, net)
    show_bounding_boxes(img, box, conf, cls, cls_dict, conf_th)
    
        

def main():

    # Initialize Caffe
    caffe.set_device(0)
    caffe.set_mode_gpu()
    net = caffe.Net(DEFAULT_PROTOTXT,DEFAULT_MODEL,caffe.TEST)

    # Build the class (index/name) dictionary from labelmap file
    lm_handle = open(DEFAULT_LABELMAP, 'r')
    lm_map = caffe_pb2.LabelMap()
    text_format.Merge(str(lm_handle.read()), lm_map)
    cls_dict = {x.label:x.display_name for x in lm_map.item}

    cap = open_cam_rtsp(uri)
    if not cap.isOpened():
        sys.exit('Failed to open camera!')
    while cap.isOpened():
    	ret,frame = cap.read()
    	read_cam_and_detect(frame,net, cls_dict, conf_th)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
