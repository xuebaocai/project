'''
Author : mengjun
Time : 2019/11/19
version: 2.0
'''

import paho.mqtt.client as mqtt
import time



def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    #print(flags)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

def on_disconnect(client, userdata, rc):
    print("disconnect")
    client.reconnect()


client = mqtt.Client()
client.username_pw_set("kinglion", "InfiniteSecret$")  # 必须设置，否则会返回「Connected with result code 4」
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.reconnect_delay_set(1, 30)

client.connect(host="192.168.153.130", port=1883, keepalive=60)
client.loop_start()

def main(label):
    while True:
        # 发布MQTT信息
        client.publish('chat','{}'.format(label),2)
        time.sleep(0.05)
        break
