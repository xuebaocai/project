#aicamera用于接收消息并写入在指定文本
#v1.0 by mengjun 5.20

import paho.mqtt.client as mqtt

class Subscribe():

    def __init__(self,host=None,topic=None):
        '''
        :param host: 代理ip
        :param topic: 主题
        '''
        self.host = host
        self.topic = topic

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code ",str(rc))

    def on_message(self,client, userdata, msg):
        # 在这里处理业务逻辑
        print(msg.topic, str(msg.payload.decode('utf-8')))
        message = str(msg.payload.decode('utf-8'))
        with open('recode.txt','w+') as f:
            f.write(message)

    def sub(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.host, 1883, 60)  # 订阅频道
        client.subscribe(self.topic)
        client.loop_forever()

if __name__ == '__main__':
    Sub = Subscribe(host='192.168.153.136',topic='zn/aicamera/alarm')
    Sub.sub()

