#aicamera鐢ㄤ簬鎺ユ敹娑堟伅骞跺啓鍏ュ湪鎸囧畾鏂囨湰
#v1.0 by mengjun 5.20

import paho.mqtt.client as mqtt
import json

class Subscribe():

    def __init__(self,host=None,topic=None):
        '''
        :param host: 浠ｇ悊ip
        :param topic: 涓婚
        '''
        self.host = host
        self.topic = topic

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code ",str(rc))

    def on_message(self,client, userdata, msg):
        # 鍦ㄨ繖閲屽鐞嗕笟鍔￠€昏緫
        global config
        global json_path
        print(msg.topic, str(msg.payload.decode('utf-8')))
        message = str(msg.payload.decode('utf-8'))
        if msg.topic.split('/')[2] == 'webpagemsg':
          if msg.topic.split('/')[3] == 'polygon':
            config['Polygon'] = message
          
          with open(json_path,'w') as f:
            
            json.dump(config,f)

    def sub(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.host, 1883, 60)  # 璁㈤槄棰戦亾
        client.subscribe(self.topic)
        client.loop_forever()

if __name__ == '__main__':
    json_path = '/home/mengjun/xianlu/tensorrt_demos/utils/config.json'
    with open(json_path,'r') as f:
       config = json.load(f)
    Sub = Subscribe(host=config['Mqtt_sub'],topic='zn/aicamera/webpagemsg/#')
    Sub.sub()

