"""camera_tf_trt.py
# to_pd tf_version==1.12.0
#train tf_version==1.15.0
2020.5.7
ssd_mobilenet_v1 16FPS
ssd_mobilenet_v2 10FPS
"""


import sys
import time
import logging
import argparse

import numpy as np
import cv2
import tensorflow as tf
import tensorflow.contrib.tensorrt as trt

from utils.camera import add_camera_args, Camera
from utils.od_utils import read_label_map, build_trt_pb, load_trt_pb, \
                           write_graph_tensorboard, detect
from utils.visualization import BBoxVisualization


# Constants
DEFAULT_MODEL = 'ssd_mobilenet_v1_egohands'
DEFAULT_LABELMAP = 'data/labelmap_voc.pbtxt'
WINDOW_NAME = 'CameraTFTRTDemo'
BBOX_COLOR = (0, 255, 0)  # green
label_map = {'1':'person','2':'hat','3':'digger','4':'truck'}

def parse_args():
    """Parse input arguments."""
    desc = ('This script captures and displays live camera video, '
            'and does real-time object detection with TF-TRT model '
            'on Jetson TX2/TX1/Nano')
    parser = argparse.ArgumentParser(description=desc)
    parser = add_camera_args(parser)
    parser.add_argument('--model', dest='model',
                        help='tf-trt object detecion model '
                        '[{}]'.format(DEFAULT_MODEL),
                        default=DEFAULT_MODEL, type=str)
    parser.add_argument('--build', dest='do_build',
                        help='re-build TRT pb file (instead of using'
                        'the previously built version)',
                        action='store_true')
    parser.add_argument('--tensorboard', dest='do_tensorboard',
                        help='write optimized graph summary to TensorBoard',
                        action='store_true')
    parser.add_argument('--labelmap', dest='labelmap_file',
                        help='[{}]'.format(DEFAULT_LABELMAP),
                        default=DEFAULT_LABELMAP, type=str)
    parser.add_argument('--num-classes', dest='num_classes',
                        help='(deprecated and not used) number of object ',
			default=4, type=int)
    parser.add_argument('--confidence', dest='conf_th',
                        help='confidence threshold [0.3]',
                        default=0.3, type=float)
    args = parser.parse_args()
    return args





def loop_and_detect(cam, tf_sess, conf_th, vis, od_type):
    """Loop, grab images from camera, and do object detection.

    # Arguments
      cam: the camera object (video source).
      tf_sess: TensorFlow/TensorRT session to run SSD object detection.
      conf_th: confidence/score threshold for object detection.
      vis: for visualization.
    """
    show_fps = True
    full_scrn = False
    fps = 0.0
    tic = time.time()
    label_cf = {}
    while True:

        img = cam.read()
        if img is not None:
            box, conf, cls = detect(img, tf_sess, conf_th, od_type=od_type)
            img = vis.draw_bboxes(img, box, conf, cls)
            toc = time.time()
            curr_fps = 1.0 / (toc - tic)
            
            
            for num,cf in zip(cls,conf):
                 label = label_map['{}'.format(num)]
                 cf = float('%.2f'%cf)
                 label_cf['{}'.format(label)] = cf
            print(label_cf,curr_fps)
            
            fps = curr_fps if fps == 0.0 else (fps*0.9 + curr_fps*0.1)
            tic = toc
            label_cf = {}


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Ask tensorflow logger not to propagate logs to parent (which causes
    # duplicated logging)
    logging.getLogger('tensorflow').propagate = False

    args = parse_args()
    logger.info('called with args: %s' % args)

    # build the class (index/name) dictionary from labelmap file
    logger.info('reading label map')
    cls_dict = read_label_map(args.labelmap_file)

    pb_path = './data/{}_trt.pb'.format(args.model)
    log_path = './logs/{}_trt'.format(args.model)
    if args.do_build:
        logger.info('building TRT graph and saving to pb: %s' % pb_path)
        build_trt_pb(args.model, pb_path)

    logger.info('opening camera device/file')
    cam = Camera(args)
    cam.open()
    if not cam.is_opened:
        sys.exit('Failed to open camera!')

    logger.info('loading TRT graph from pb: %s' % pb_path)
    trt_graph = load_trt_pb(pb_path)

    logger.info('starting up TensorFlow session')
    tf_config = tf.ConfigProto()
    tf_config.gpu_options.allow_growth = True
    tf_sess = tf.Session(config=tf_config, graph=trt_graph)

    if args.do_tensorboard:
        logger.info('writing graph summary to TensorBoard')
        write_graph_tensorboard(tf_sess, log_path)

    logger.info('warming up the TRT graph with a dummy image')
    od_type = 'faster_rcnn' if 'faster_rcnn' in args.model else 'ssd'
    dummy_img = np.zeros((720, 1280, 3), dtype=np.uint8)
    _, _, _ = detect(dummy_img, tf_sess, conf_th=.3, od_type=od_type)

    cam.start()  # ask the camera to start grabbing images

    # grab image and do object detection (until stopped by user)
    logger.info('starting to loop and detect')
    vis = BBoxVisualization(cls_dict)

    loop_and_detect(cam, tf_sess, args.conf_th, vis, od_type=od_type)

    logger.info('cleaning up')
    cam.stop()  # terminate the sub-thread in camera
    tf_sess.close()
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
