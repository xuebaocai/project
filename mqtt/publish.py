# 2020.5.20
# aicamera用于发送消息
#v1.0 by mengjun

import paho.mqtt.client as mqtt
import json
import numpy as np
import time
import sys
import io
from PIL import Image
from imutils import opencv2matplotlib
import cv2

class Publish():

    def __init__(self,host=None,topic=None,send_msg=False,send_img=False,img=None,msg=None):
        '''
        
        :param host: 代理ip
        :param topic: 主题
        :param send_msg: 是否发送文字
        :param send_img: 是否发送图片
        :param img: 图片地址
        :param msg: 文字
        '''
        self.send_img = send_img
        self.send_msg = send_msg
        self.host = host
        self.topic = topic
        self.msg = msg
        self.img = img

    def pil_image_to_byte_array(self,image):
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, "PNG")
        return imgByteArr.getvalue()


    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code " + str(rc))


    def on_disconnect(self,client, userdata, rc):
        # print("disconnect")
        client.reconnect()


    def send(self):
        client = mqtt.Client()
        #client.username_pw_set("aicamer_{}".format(device_id), "aicameraSecret$#")  # "admin", "password"
        client.on_connect = self.on_connect

        #client.will_set('zn/aicamera/{}/{}/alarm'.format(device_id, serial_id), 'Last will message', 0, False)

        client.on_disconnect = self.on_disconnect
        client.reconnect_delay_set(1, 30)

        client.connect(host=self.host, port=1883, keepalive=60)
        client.loop_start()
        # 发布MQTT信息
        if self.send_msg == True:

            # alarm
            client.publish(topic=self.topic, payload=self.msg, qos=2)
            time.sleep(0.1)

        if self.send_img == True:
            # image
            image = cv2.imread(self.img)
            np_array_RGB = opencv2matplotlib(image)  # Convert to RGB
            image = Image.fromarray(np_array_RGB)  # PIL image
            byte_array = self.pil_image_to_byte_array(image)
            client.publish(topic=self.topic, payload=byte_array, qos=2)
            time.sleep(0.1)

        client.loop_stop()


if __name__ == '__main__':
    pub = Publish(host='192.168.153.136',topic='zn/aicamera/image',send_msg=False,send_img=True,msg=None,img='C:/Users/windows10/Desktop/test_imgs/hat.jpg')
    pub.send()

