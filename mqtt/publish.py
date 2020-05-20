# 2020.4.23
#aicamera
import paho.mqtt.client as mqtt
import json
import numpy as np
import time
import sys
import io
from PIL import Image
from imutils import opencv2matplotlib
import cv2

def pil_image_to_byte_array(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, "PNG")
    return imgByteArr.getvalue()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
   
def on_disconnect(client, userdata, rc):
    #print("disconnect")
    client.reconnect()

def main(alarm,image,device_id=1,serial_id=10,send=False):
    client = mqtt.Client()
    client.username_pw_set("aicamer_{}".format(device_id), "aicameraSecret$#")  # "admin", "password"
    client.on_connect = on_connect
    
    client.will_set('zn/aicamera/{}/{}/alarm'.format(device_id,serial_id), 'Last will message', 0, False)
    
    client.on_disconnect = on_disconnect
    client.reconnect_delay_set(1, 30)

    client.connect(host="183.129.253.180", port=1883, keepalive=60)
    client.loop_start()
    if send == True:
        # 发布MQTT信息
        #alarm
        client.publish(topic='zn/aicamera/{}/{}/alarm'.format(device_id,serial_id),payload=alarm,qos=2)
        #image
        np_array_RGB = opencv2matplotlib(image)  # Convert to RGB
        image = Image.fromarray(np_array_RGB)  # PIL image
        byte_array = pil_image_to_byte_array(image)
        client.publish(topic='zn/aicamera/{}/{}/alarm'.format(device_id, serial_id), payload=byte_array, qos=2)

    client.loop_stop()

if __name__=='__main__':
    main(alarm='vvv',send=True)
