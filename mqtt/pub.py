import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
from PIL import Image
import cv2
import io
from imutils import opencv2matplotlib


image_path = '/home/mengjun/project/0.jpg'

def pil_image_to_byte_array(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, "PNG")
    return imgByteArr.getvalue()

image = cv2.imread(image_path)
np_array_RGB = opencv2matplotlib(image)  # Convert to RGB
image = Image.fromarray(np_array_RGB)  # PIL image
byte_array = pil_image_to_byte_array(image)

#idx = 0  # 往paho/temperature 一直发送内容
while True:
    print("send success")
    publish.single("paho/temperature",
                   payload=byte_array,
                   hostname="localhost",
                   client_id="lora1",
                   # qos = 0,
                   # tls=tls,
                   port=1883,
                   protocol=mqtt.MQTTv311)
    
    time.sleep(0.25)
    break
