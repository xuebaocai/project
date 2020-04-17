import paho.mqtt.client as mqtt

from PIL import Image
import cv2
import io

def byte_array_to_pil_image(byte_array):
    return Image.open(io.BytesIO(byte_array))


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code ",str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # 在这里处理业务逻辑
    #print(msg.topic, str(msg.payload.decode('utf-8')))
    image = byte_array_to_pil_image(msg.payload)
    image = image.convert("RGB")
    image.save('/home/mengjun/project/1.jpg')


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)  # 订阅频道
client.subscribe("paho/temperature")

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

