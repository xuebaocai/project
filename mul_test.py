import time
import multiprocessing as mp
import cv2
import mul_ssd
import caffe
from caffe.proto import caffe_pb2

CAFFE_ROOT = '/home/junmeng/project/ssd-caffe/'
sys.path.insert(0, CAFFE_ROOT + 'python')
DEFAULT_PROTOTXT = CAFFE_ROOT + 'models/googlenet_fc/coco/SSD_300x300/deploy.prototxt'
DEFAULT_MODEL    = CAFFE_ROOT + 'models/googlenet_fc/coco/SSD_300x300/deploy.caffemodel'
DEFAULT_LABELMAP = CAFFE_ROOT + 'data/coco/labelmap_coco.prototxt'
conf_th =0.3

# Initialize Caffe
caffe.set_device(0)
caffe.set_mode_gpu()
net = caffe.Net(DEFAULT_PROTOTXT ,DEFAULT_MODEL ,caffe.TEST)
# Build the class (index/name) dictionary from labelmap file
lm_handle = open(DEFAULT_LABELMAP, 'r')
lm_map = caffe_pb2.LabelMap()
text_format.Merge(str(lm_handle.read()), lm_map)
cls_dict = {x.label :x.display_name for x in lm_map.item}

def image_put(q, dev):
    cap = cv2.VideoCapture(dev)
    print(cap.isOpened())
    while cap.isOpened():
        q.put(cap.read()[1])
        q.get() if q.qsize() > 1 else time.sleep(0.01)


def image_get(q, window_name):
    cv2.namedWindow(window_name, flags=cv2.WINDOW_FREERATIO)
    while True:
        frame = q.get()
        mul_ssd.read_cam_and_detect(net, cls_dict, conf_th, frame)
        cv2.imshow('{}'.format(window_name), frame)
        K = cv2.waitKey(1)
        if K == 27:
            break
    cv2.destroyAllWindows()


def run_single_camera():
    dev = 0
    mp.set_start_method(method='spawn')  # init
    queue = mp.Queue(maxsize=2)
    processes = [mp.Process(target=image_put, args=(queue, dev)),
                 mp.Process(target=image_get, args=(queue, dev))]

    [process.start() for process in processes]
    [process.join() for process in processes]

def run_multi_camera():
    dev_list = [0,1]

    mp.set_start_method(method='spawn')  # init
    queues = [mp.Queue(maxsize=4) for _ in dev_list]

    processes = []

    for queue, dev in zip(queues, dev_list):
        processes.append(mp.Process(target=image_put, args=(queue, dev)))
        processes.append(mp.Process(target=image_get, args=(queue, dev)))

    for process in processes:
        process.daemon = True
        process.start()
    for process in processes:
        process.join()

def run():

    run_multi_camera() # with 1 + n threads



if __name__ == '__main__':


    run()


