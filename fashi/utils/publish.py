#2020.7.30
# aicamera mqtt publish
# v1.1 by mengjun

import paho.mqtt.client as mqtt
import json
import numpy as np
import time
import sys
import io
from PIL import Image

import cv2
import json

class Publish():

    def __init__(self,host=None):

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

    def send_msg(self,topic,msg,Zone,device_id):
        client = mqtt.Client()
        #client.username_pw_set("aicamer_{}".format(device_id), "aicameraSecret$#")  # "admin", "password"
        client.on_connect = self.on_connect
        ai_device_id = str(Zone) + str(device_id)
        will_topic = "zn/ai_spxwfx/{}/network".format(ai_device_id)
        will_msg = json.dumps({
                    "online": 0})
        client.will_set(will_topic, will_msg, 0, False)

        client.on_disconnect = self.on_disconnect
        client.reconnect_delay_set(1, 30)

        client.connect(host=self.host, port=1883, keepalive=60)
        client.loop_start()
        # alarm
        client.publish(topic=topic, payload=msg, qos=2)
        time.sleep(0.1)
        client.loop_stop()

if __name__ == '__main__':

    pub = Publish(host='10.150.38.141')
   # msg = json.dumps({'Pologon':[[20,20],[20,400],[400,20],[400,400]]})
   # pub.send_msg(topic='zn/aicamera/webpagemsg/polygon',msg=msg)

    msg = json.dumps('10')
    pub.send_msg(topic='zn/aicamera/',msg=msg)

    #pub.send_img(topic='msg',img='/home/mengjun/mydata/JPEGImages/person_0.jpg')
