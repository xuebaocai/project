#2020.9.28
# aicamera mqtt publish
# v1.2 by mengjun

import paho.mqtt.client as mqtt
import json
import numpy as np
import time
import sys
import io
from PIL import Image
from imutils import opencv2matplotlib
import cv2
import json

class Publish():

    def __init__(self,host=None):
        '''
        
        :param host: 浠ｇ悊ip
        :param topic: 涓婚
        :param img: 鍥剧墖鍦板潃
        :param msg: 鏂囧瓧
        '''
        self.host = host

    def pil_image_to_byte_array(self,image):
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, "PNG")
        return imgByteArr.getvalue()


    def on_connect(self,client, userdata, flags, rc):
        return rc


    def on_disconnect(self,client, userdata, rc):
        # print("disconnect")
        client.reconnect()


    def send_img(self,topic,img):
        client = mqtt.Client()
        #client.username_pw_set("aicamer_{}".format(device_id), "aicameraSecret$#")  # "admin", "password"
        client.on_connect = self.on_connect

        #client.will_set('zn/aicamera/{}/{}/alarm'.format(device_id, serial_id), 'Last will message', 0, False)

        client.on_disconnect = self.on_disconnect
        client.reconnect_delay_set(1, 30)

        client.connect(host=self.host, port=1883, keepalive=60)
        client.loop_start()
        # image
        np_array_RGB = opencv2matplotlib(img)  # Convert to RGB
        image = Image.fromarray(np_array_RGB)  # PIL image
        byte_array = self.pil_image_to_byte_array(image)
        client.publish(topic=topic, payload=byte_array, qos=2)
        time.sleep(0.1)

        client.loop_stop()

    def send_msg(self,topic,msg):
        client = mqtt.Client()
        #client.username_pw_set("aicamer_{}".format(device_id), "aicameraSecret$#")  # "admin", "password"
        client.on_connect = self.on_connect

        #client.will_set('zn/aicamera/{}/{}/alarm'.format(device_id, serial_id), 'Last will message', 0, False)

        client.on_disconnect = self.on_disconnect
        client.reconnect_delay_set(1, 30)

        client.connect(host=self.host, port=1883, keepalive=60)
        client.loop_start()
        # alarm
        client.publish(topic=topic, payload=msg, qos=2)
        time.sleep(0.1)
        client.loop_stop()

if __name__ == '__main__':
    json_path = '/home/mengjun/xianlu/tensorrt_demos/utils/config.json'
    with open(json_path,'r') as f:
      config = json.load(f)
    pub = Publish(host=config['Mqtt_pub'])
    pub.send_msg(topic='zn/aicamera/webpagemsg/polygon',msg='[10,50,47,69]')
    #pub.send_img(topic='msg',img='/home/mengjun/mydata/JPEGImages/person_0.jpg')


