import paho.mqtt.client as mqtt
import json,time
import common.zoneserver_message_pb2 as zm_pb2
from PIL import Image, ImageDraw,ImageFont
import io

def show_img(img_bytes,boxes,confs):
   print(boxes)
   image = Image.open(io.BytesIO(img_bytes))
   image = image.convert("RGB")
   draw = ImageDraw.Draw(image)
   font = ImageFont.truetype('MSYHMONO.ttf', 24)
   draw.text([int((boxes[0][0]+boxes[0][2])/2 - 20) ,int((boxes[0][1] +boxes[0][3])/2)], 
     text='h_f:{},s_f:{},p_f:{}'.format(round(confs[0][0],2),round(confs[0][1],2),round(confs[0][2],2)), fill=(255, 0, 0),font=font)
   draw.rectangle((boxes[0][0],boxes[0][1], boxes[0][2],boxes[0][3]),fill=None, outline="red")
   str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
   image.save('/home/a/project/result/{}.jpg'.format(str_time))
   print('save done')
   
   
class Subscribe():

    def __init__(self,host=None,topic=None):
        self.host = host
        self.topic = topic

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code ",str(rc))

    def on_message(self,client, userdata, msg):
        print('topic:',msg.topic)
        result_data = zm_pb2.HelSuiDetectionData()
        result_data.ParseFromString(msg.payload)
        boxes = []
        confs = []
        print(result_data.alarm_flag)
        if result_data.alarm_flag:
          boxes.append([result_data.single_data_list[0].pedestrian_rectangle.lt_x,
            result_data.single_data_list[0].pedestrian_rectangle.lt_y,
            result_data.single_data_list[0].pedestrian_rectangle.rb_x,
            result_data.single_data_list[0].pedestrian_rectangle.rb_y,] )
          confs.append([result_data.single_data_list[0].helmet_alarm_confidence,
            result_data.single_data_list[0].suit_alarm_confidence,
            result_data.single_data_list[0].pedestrian_confidence,])
        #print(result_data.single_data_list[0])
        
          show_img(result_data.img,boxes,confs)
        
    def sub(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.host, 1883, 60)  # 鐠併垽妲勬０鎴︿壕
        client.subscribe(self.topic)
        client.loop_forever()

if __name__ == '__main__':
    Sub = Subscribe(host='183.129.235.180',topic='zs/helmetSuit/channel1/helmet_suit/out')
    Sub.sub()
