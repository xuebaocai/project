import os
import cv2
from lib.utils import get_ground_truthes,plot_precision,plot_success,plot_list_success,plot_list_precision
import numpy as np

class MessageItem(object):
    # 用于封装信息的类,包含图片和其他信息
    def __init__(self, frame, message):
        self._frame = frame
        self._message = message

    def getFrame(self):
        # 图片信息
        return self._frame

    def getMessage(self):
        # 文字信息,json格式
        return self._message


class Tracker(object):
    '''
    追踪者模块,用于追踪指定目标
    '''

    def __init__(self, tracker_type="BOOSTING", draw_coord=True):
        '''
        初始化追踪器种类
        '''
        # 获得opencv版本
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
        self.tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
        self.tracker_type = tracker_type
        self.isWorking = False
        self.draw_coord = draw_coord
        # 构造追踪器
        if int(major_ver) < 3:
            self.tracker = cv2.Tracker_create(tracker_type)
        else:
            if tracker_type == 'BOOSTING':
                #6.2fps
                self.tracker = cv2.TrackerBoosting_create()
            if tracker_type == 'MIL':
                #1.7fps
                self.tracker = cv2.TrackerMIL_create()
            if tracker_type == 'KCF':
                #1.7fps
                self.tracker = cv2.TrackerKCF_create()
            if tracker_type == 'TLD':
                #1.7fps
                self.tracker = cv2.TrackerTLD_create()
            if tracker_type == 'MEDIANFLOW':
                #1.8fps
                self.tracker = cv2.TrackerMedianFlow_create()
                #效果好

    def initWorking(self, frame, box):
        '''
        追踪器工作初始化
        frame:初始化追踪画面
        box:追踪的区域
        '''
        if not self.tracker:
            raise Exception("追踪器未初始化")
        status = self.tracker.init(frame, box)
        if not status:
            raise Exception("追踪器工作初始化失败")
        self.coord = box
        self.isWorking = True

    def track(self, frame):
        '''
        开启追踪
        '''
        message = None
        if self.isWorking:
            status, self.coord = self.tracker.update(frame)
            bbox = int(self.coord[0]), int(self.coord[1]),int(self.coord[2]),int(self.coord[3])
        return bbox

if __name__ == '__main__':

    data_dir='C:/Users/17321/Desktop/OTB100/OTB100_test'
    img_dir = '/digger/'
    #model = 'KCF'
    models = ['TLD','BOOSTING','KCF']
    result_dir = 'C:/Users/17321/Desktop/pyCFTrackers-master/results/' + models[0] + '/'

    poses_list  = []
    for model in models:
        gTracker = Tracker(tracker_type=model)
        img = cv2.imread(data_dir+ img_dir + 'img/'+'0000.jpg')
        gts = get_ground_truthes(data_dir+img_dir)
        gTracker.initWorking(img, (gts[0][0],gts[0][1],gts[0][2],gts[0][3]))



        poses = []
        index = 1
        for img_path in sorted(os.listdir(data_dir+img_dir+'/img/')):
            if img_path != '0000.jpg':
                img = cv2.imread(data_dir+img_dir+'/img/'+img_path)
                bbox = gTracker.track(img)
                x,y,w,h = bbox

                x_t,y_t,w_t,h_t = gts[index]
                index += 1
                cv2.rectangle(img,(x_t,y_t),(x_t+w_t,y_t+h_t),(0,255,0),1)
                cv2.rectangle(img,(x,y),(x+w,y+h),(255, 0, 0),2)
                cv2.imshow('demo',img)
                cv2.waitKey(1)
                poses.append(np.array([int(x), int(y), int(w), int(h)]))

        poses = np.array(poses)
        poses_list.append(poses)
    if os.path.exists(result_dir) is False:
        os.mkdir(result_dir)
    plot_list_success(gts,poses_list,os.path.join(result_dir,model+'_success.jpg'))
    plot_list_precision(gts,poses_list,os.path.join(result_dir,model+'_precision.jpg'))