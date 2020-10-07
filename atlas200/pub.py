import paho.mqtt.client as mqtt
import numpy as np
import time
import common.middle_data_message_pb2 as mdm_pb2

class Publish():

    def __init__(self,host=None):
        self.host = host

    def on_connect(self,client, userdata, flags, rc):
        return rc


    def on_disconnect(self,client, userdata, rc):
        # print("disconnect")
        client.reconnect()


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
        request = mdm_pb2.PolygonVertexData()
        data = request.single_point_list.add()
        data.x = msg[0]
        data.y = msg[1]
        client.publish(topic=topic, payload=request.SerializeToString(), qos=0)
        time.sleep(0.1)
        client.loop_stop()

if __name__ == '__main__':
    pub = Publish('183.129.235.180')
    pub.send_msg(topic='zs/webpagemsg/absence/channel1/polygonvertex/out',msg=[10,20])

    #pub.send_img(topic='msg',img='/home/mengjun/mydata/JPEGImages/person_0.jpg')i
