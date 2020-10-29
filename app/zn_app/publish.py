import paho.mqtt.client as mqtt
import json
import time


#消息发送类
class Publish():

    def __init__(self, host=None):
        '''
        :param host: mqtt地址

        '''
        self.host = host


    def on_connect(self, client, userdata, flags, rc):
        self.flag = rc
        return rc

    def on_disconnect(self, client, userdata, rc):
        # print("disconnect")
        client.reconnect()

    def is_connected(self):
        return self.flag

    def send_msg(self, topic, msg):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.reconnect_delay_set(1, 30)

        client.connect(host=self.host, port=1883, keepalive=60)
        client.loop_start()
        # 消息发送
        client.publish(topic=topic, payload=msg, qos=2)
        time.sleep(0.1)
        client.loop_stop()


if __name__ == '__main__':
    pub = Publish(host='10.150.28.81')
    pub.send_msg(topic='zs/polygonvertex/absence/channel{}/out'.format(1),
                          msg = 'msg')
    print(pub.is_connected())

