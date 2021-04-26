from .ssd_classes import get_cls_dict, COCO_CLASSES_LIST
from .visualization import BBoxVisualization
from .publish import Publish
import utils.InterfaceMessage_pb2 as im_pb2
from imutils import opencv2matplotlib
from PIL import Image
import io
import cv2
import time
from datetime import datetime, timedelta


def pil_image_to_byte_array(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, "PNG")
    return imgByteArr.getvalue()


def start_end_status(start, history_data, last_alarm_time, alarm_interval_time=15):
    current_time = time.time()
    detection_num = 15
    if start:
        if int(1) not in history_data:
            slide_history(1, history_data)
            return str('start')
        else:
            if current_time < (last_alarm_time + int(alarm_interval_time)):

                history_add = sum(history_data[-detection_num:])
                if history_add < 8 and current_time >= (last_alarm_time + int(alarm_interval_time)):
                    set_history_data

                    return str('end')
                else:
                    return str('lasting')
            else:
                set_history_data
                return str('end')
    else:
        if current_time < (last_alarm_time + int(alarm_interval_time)):
            history_add = sum(history_data[-detection_num:])
            if history_add < 8 and current_time >= (last_alarm_time + int(alarm_interval_time)):
                set_history_data

                return str('end')

        else:
            return str('end')


# 历史数据滑动函数
def slide_history(alarm_flag, history_data):
    history_data.pop(0)
    history_data.append(alarm_flag)


# 初始化历史数据
def set_history_data():
    history_data = [0] * 40


def end_topic(last_topic_time,last_alarm_type,Zone,Channel,device_id,pub):
    print('topic_end')
    
    baseData = im_pb2.BaseData()
    baseData.app_id = Zone
    baseData.channel_id = 'channel' + str(Channel)
    baseData.fps = 20
    baseData.timestamp = time.time()
    baseData.frame_id = last_topic_time
    print(baseData.frame_id)
    detectionCommonData = im_pb2.DetectionCommonData(base_data=baseData)
    detectionCommonDataDict = {}
    detectionCommonDataDict[Zone] = detectionCommonData
    result_data = im_pb2.GeneralDetectionMapData(general_map_data=detectionCommonDataDict)
    topic = 'zs/' + Zone + '/' + 'channel' + str(Channel) + '/' + last_alarm_type + '/out'
    print(topic)
    pub.send_msg(
        topic='zs/' + Zone + '/' + 'channel' + str(Channel) + '/' + last_alarm_type + '/out',
        msg=result_data.SerializeToString(),Zone=Zone,device_id=device_id)



class Data_sys():

    def __init__(self):
        self.last_fire_alarm_time = None
        self.last_fire_topic_time = None
        self.last_fire_alarm_type = None
        self.last_person_alarm_time = None
        self.last_person_topic_time = None
        self.last_person_alarm_type = None
        self.fire_history_data = [0] * 40
        self.person_history_data = [0] * 40

    def dataSynchronization(self, result, img_list, model, alarm_type, Zone, Channel,device_id, pub, Polygon_list):
        
        cls_dict = get_cls_dict(model.split('_')[-1])
        vis = BBoxVisualization(cls_dict)

        for i in range(len(result)):
            boxes, confs, clss = result[i][0], result[i][1], result[i][2]
            img, txt = vis.draw_bboxes(img_list[0][i], boxes, confs, clss)
            alarm = str(txt).split(' ')[0]
            print(alarm)

            if alarm in COCO_CLASSES_LIST:
                if alarm == 'fire':
                    np_array_RGB = opencv2matplotlib(img)  # Convert to RGB
                    image = Image.fromarray(np_array_RGB)  # PIL image
                    byte_array = pil_image_to_byte_array(image)
                    baseData = im_pb2.BaseData()
                    baseData.img = byte_array
                    baseData.app_id = Zone
                    baseData.channel_id = 'channel' + str(Channel)
                    baseData.fps = 20
                    baseData.timestamp = time.time()
                    self.last_fire_alarm_time = time.time()
                    baseData.alarm_type = 'Firesmoke'
                    self.last_fire_alarm_type = baseData.alarm_type
                    current_status = start_end_status(True, self.fire_history_data, baseData.timestamp, 15)
                    if current_status == 'start':
                        baseData.frame_id = time.strftime('%H%M%S', time.localtime(time.time()))
                        detectionCommonData = im_pb2.DetectionCommonData(base_data=baseData)
                        detectionCommonDataDict = {}
                        detectionCommonDataDict[Zone] = detectionCommonData
                        result_data = im_pb2.GeneralDetectionMapData(general_map_data=detectionCommonDataDict)
                        self.last_fire_topic_time = baseData.frame_id
                        print('topic_start')
                        pub.send_msg(topic='zs/' + Zone + '/' + 'channel' + str(Channel) + '/' + 'Firesmoke' + '/out',
                                     msg=result_data.SerializeToString(),Zone=Zone,device_id=device_id)

                    else:
                        slide_history(1, self.fire_history_data)

                if alarm == 'person':
                    np_array_RGB = opencv2matplotlib(img)  # Convert to RGB
                    image = Image.fromarray(np_array_RGB)  # PIL image
                    byte_array = pil_image_to_byte_array(image)
                    baseData = im_pb2.BaseData()
                    baseData.img = byte_array
                    baseData.app_id = Zone
                    baseData.channel_id = 'channel' + str(Channel)
                    baseData.fps = 20
                    baseData.timestamp = time.time()
                    self.last_person_alarm_time = time.time()
                    baseData.alarm_type = 'Personnelfall'
                    self.last_person_alarm_type = baseData.alarm_type
                    current_status = start_end_status(True, self.person_history_data, baseData.timestamp, 15)
                    if current_status == 'start':
                        baseData.frame_id = time.strftime('%H%M%S', time.localtime(time.time()))
                        detectionCommonData = im_pb2.DetectionCommonData(base_data=baseData)
                        detectionCommonDataDict = {}
                        detectionCommonDataDict[Zone] = detectionCommonData
                        result_data = im_pb2.GeneralDetectionMapData(general_map_data=detectionCommonDataDict)
                        self.last_person_topic_time = baseData.frame_id
                        print('topic_start')
                        print(baseData.frame_id)
                        topic = 'zs/' + Zone + '/' + 'channel' + str(Channel) + '/' + 'Personnelfall' + '/out'
                        print(topic)
                        pub.send_msg(
                            topic='zs/' + Zone + '/' + 'channel' + str(Channel) + '/' + 'Personnelfall' + '/out',
                            msg=result_data.SerializeToString(),Zone=Zone,device_id=device_id)

                    else:
                        slide_history(1, self.person_history_data)

            else:
                slide_history(0, self.fire_history_data)
                slide_history(0, self.person_history_data)
                if self.last_person_alarm_time is not None:
                    current_status = start_end_status(False, self.person_history_data, self.last_person_alarm_time, 15)
                    if current_status == 'end':
                        self.last_person_alarm_time = None
                        end_topic( self.last_person_topic_time, self.last_person_alarm_type, Zone,Channel,device_id, pub)

                if self.last_fire_alarm_time is not None:
                    current_status = start_end_status(False, self.fire_history_data, self.last_fire_alarm_time, 15)
                    if current_status == 'end':
                        self.last_fire_alarm_time = None
                        end_topic(self.last_fire_topic_time,self.last_fire_alarm_type,Zone,Channel,device_id,pub)






