import paho.mqtt.client as mqtt
import json, time
import common.zoneserver_message_pb2 as zm_pb2
from PIL import Image, ImageDraw, ImageFont
import io
import cv2

def HelSui_show_img(msg):
    result_data = zm_pb2.HelSuiDetectionData()
    result_data.ParseFromString(msg.payload)
    boxes = []
    confs = []
    print(result_data.alarm_flag)
    if result_data.alarm_flag :
        for i in range(len(result_data.single_data_list)):
            boxes.append([result_data.single_data_list[i].pedestrian_rectangle.lt_x,
                          result_data.single_data_list[i].pedestrian_rectangle.lt_y,
                          result_data.single_data_list[i].pedestrian_rectangle.rb_x,
                          result_data.single_data_list[i].pedestrian_rectangle.rb_y, ])
            confs.append([result_data.single_data_list[i].helmet_alarm_confidence,
                          result_data.single_data_list[i].suit_alarm_confidence,
                          result_data.single_data_list[i].pedestrian_confidence, ])

        image = Image.open(io.BytesIO(result_data.img))
        image = image.convert("RGB")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('MSYHMONO.ttf', 24)
        for i in range(len(result_data.single_data_list)):
            draw.text([int((boxes[i][0] + boxes[i][2]) / 2 - 20), int((boxes[i][1] + boxes[i][3]) / 2)],
                      text='h_f:{},s_f:{},p_f:{}'.format(round(confs[i][0], 2), round(confs[i][1], 2), round(confs[i][2], 2)),
                      fill=(255, 0, 0), font=font)
            draw.rectangle((boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]), fill=None, outline="red")
            str_time = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
            image.save('C:/Users/17321/Desktop/a200_result/HelSui/{}.jpg'.format(str_time))
        print('save done')


def falldown_show_img(msg):
    result_data = zm_pb2.ClimbFallDetectionData()
    result_data.ParseFromString(msg.payload)
    boxes = []
    confs = []
    print(result_data)
    if result_data.alarm_flag:
        for i in range(len(result_data.single_data_list)):
            boxes.append([result_data.single_data_list[i].climb_fall_rectangle.lt_x,
                          result_data.single_data_list[i].climb_fall_rectangle.lt_y,
                          result_data.single_data_list[i].climb_fall_rectangle.rb_x,
                          result_data.single_data_list[i].climb_fall_rectangle.rb_y, ])
            confs.append([result_data.single_data_list[i].climb_confidence,
                          result_data.single_data_list[i].fall_confidence,])

        image = Image.open(io.BytesIO(result_data.img))
        image = image.convert("RGB")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('MSYHMONO.ttf', 24)
        for i in range(len(result_data.single_data_list)):
            draw.text([int((boxes[i][0] + boxes[i][2]) / 2 - 20), int((boxes[i][1] + boxes[i][3]) / 2)],
                      text='cli_f:{},fall_f:{}'.format(round(confs[i][0], 2), round(confs[i][1], 2)),
                      fill=(255, 0, 0), font=font)
            draw.rectangle((boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]), fill=None, outline="red")
            str_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
            image.save('C:/Users/17321/Desktop/a200_result/falldown/{}.jpg'.format(str_time))
            img = cv2.imread('C:/Users/17321/Desktop/a200_result/falldown/{}.jpg'.format(str_time))
        print('save done')


def absence_show_img(msg):
    result_data = zm_pb2.AbsenceDetectionData()
    result_data.ParseFromString(msg.payload)
    boxes = []
    confs = []
    print(result_data.alarm_flag)
    if result_data.alarm_flag :
        for i in range(len(result_data.single_data_list)):
            boxes.append([result_data.single_data_list[i].pedestrian_rectangle.lt_x,
                          result_data.single_data_list[i].pedestrian_rectangle.lt_y,
                          result_data.single_data_list[i].pedestrian_rectangle.rb_x,
                          result_data.single_data_list[i].pedestrian_rectangle.rb_y, ])
            confs.append([result_data.single_data_list[i].pedestrian_confidence,
                          ])

        image = Image.open(io.BytesIO(result_data.img))
        image = image.convert("RGB")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('MSYHMONO.ttf', 24)
        for i in range(len(result_data.single_data_list)):
            draw.text([int((boxes[i][0] + boxes[i][2]) / 2 - 20), int((boxes[i][1] + boxes[i][3]) / 2)],
                      text='p_f:{}'.format(round(confs[i][0], 2)),
                      fill=(255, 0, 0), font=font)
            draw.rectangle((boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]), fill=None, outline="red")
            str_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
            image.save('C:/Users/17321/Desktop/a200_result/absence/{}.jpg'.format(str_time))

            # 边界框
            img = cv2.imread('C:/Users/17321/Desktop/a200_result/absence/{}.jpg'.format(str_time))
            cv2.rectangle(img, frame, (500,250), (990,640), (255, 0, 0), 2)
            cv2.imwrite('C:/Users/17321/Desktop/a200_result/absence/{}.jpg'.format(str_time), img)
        print('save done')

def smoking_call_sleep_show_img(msg):
    result_data = zm_pb2.SmokingCallSleepDetectionData()
    result_data.ParseFromString(msg.payload)
    boxes = []
    confs = []
    print(result_data.alarm_flag)
    if result_data.alarm_flag :
        for i in range(len(result_data.single_data_list)):
            boxes.append([result_data.single_data_list[i].pedestrian_rectangle.lt_x,
                          result_data.single_data_list[i].pedestrian_rectangle.lt_y,
                          result_data.single_data_list[i].pedestrian_rectangle.rb_x,
                          result_data.single_data_list[i].pedestrian_rectangle.rb_y, ])
            confs.append([result_data.single_data_list[i].cellphone_alarm_confidence,
                          result_data.single_data_list[i].sleep_alarm_confidence,
                          result_data.single_data_list[i].smoking_alarm_confidence,
                          ])

        image = Image.open(io.BytesIO(result_data.img))
        image = image.convert("RGB")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('MSYHMONO.ttf', 24)
        for i in range(len(result_data.single_data_list)):
            draw.text([int((boxes[i][0] + boxes[i][2]) / 2 - 20), int((boxes[i][1] + boxes[i][3]) / 2)],
                      text='cell_f:{},sleep_f:{},smoking_f:{}'.format(round(confs[i][0], 2),round(confs[i][1], 2),round(confs[i][2], 2)),
                      fill=(255, 0, 0), font=font)
            draw.rectangle((boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]), fill=None, outline="red")
            str_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
            image.save('C:/Users/17321/Desktop/a200_result/smoking_call_sleep/{}.jpg'.format(str_time))
        print('save done')

def boundary_intrude_show_img(msg):
    result_data = zm_pb2.BouIntDetectionData()
    result_data.ParseFromString(msg.payload)
    boxes = []
    confs = []
    print(result_data.alarm_flag)
    if result_data.alarm_flag :
        for i in range(len(result_data.single_data_list)):
            boxes.append([result_data.single_data_list[i].pedestrian_rectangle.lt_x,
                          result_data.single_data_list[i].pedestrian_rectangle.lt_y,
                          result_data.single_data_list[i].pedestrian_rectangle.rb_x,
                          result_data.single_data_list[i].pedestrian_rectangle.rb_y, ])
            confs.append([result_data.single_data_list[i].boundary_alarm_confidence,
                          result_data.single_data_list[i].pedestrian_confidence,
                          ])

        image = Image.open(io.BytesIO(result_data.img))
        image = image.convert("RGB")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('MSYHMONO.ttf', 24)
        for i in range(len(result_data.single_data_list)):
            draw.text([int((boxes[i][0] + boxes[i][2]) / 2 - 20), int((boxes[i][1] + boxes[i][3]) / 2)],
                      text='b_f:{},p_f:{}'.format(round(confs[i][0], 2),round(confs[i][1], 2)),
                      fill=(255, 0, 0), font=font)
            draw.rectangle((boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]), fill=None, outline="red")


            str_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
            image.save('C:/Users/17321/Desktop/a200_result/boundary_intrude/{}.jpg'.format(str_time))
            # 边界框
            img = cv2.imread('C:/Users/17321/Desktop/a200_result/boundary_intrude/{}.jpg'.format(str_time))
            cv2.rectangle(img, frame, (500,250), (990,640), (255, 0, 0), 2)
            cv2.imwrite('C:/Users/17321/Desktop/a200_result/boundary_intrude/{}.jpg'.format(str_time), img)
        print('save done')

class Subscribe():

    def __init__(self, host=None, topic=None):
        self.host = host
        self.topic = topic

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code ", str(rc))

    def on_message(self, client, userdata, msg):
        print('topic:', msg.topic)
        alarm_type =msg.topic.split('/')[3]
        if alarm_type == 'helmet_suit':
            HelSui_show_img(msg)
        elif alarm_type == 'ClimbFall':
            falldwon_show_img(msg)
        elif alarm_type == 'absence':
            absence_show_img(msg)
        elif alarm_type == 'SmokingCallSleep':
            smoking_call_sleep_show_img(msg)
        elif alarm_type == 'boundary_intrude':
            boundary_intrude_show_img(msg)

    def sub(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.host, 1883, 60)  # 鐠併垽妲勬０鎴︿壕
        client.subscribe(self.topic)
        client.loop_forever()


if __name__ == '__main__':
    #topic = 'zs/helmetSuit/channel1/helmet_suit/out'
    #topic = 'zs/absence/channel1/absence/out'
    #topic = 'zs/fallDown/channel1/ClimbFall/out'
    topic = 'zs/smoking/channel1/SmokingCallSleep/out'
    #topic = 'zs/boundaryIntrude/channel1/boundary_intrude/out'
    Sub = Subscribe(host='10.150.38.141', topic=topic)
    Sub.sub()
