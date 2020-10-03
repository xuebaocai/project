from apscheduler.schedulers.blocking import BlockingScheduler
from config import Host,Latit,Longit,Distance,Power
from geopy.distance import geodesic
from control.camera_power import gps_read,power_read
from mqtt.publish import Publish
import threading
import json

json_path = '/home/mengjun/xianlu/tensorrt_demos/utils/config.json'
with open(json_path,'r') as f:
   config = json.load(f)

#print(config)

pub = Publish(host=config['Mqtt_pub'])

def func(latit,longit,power):
    pub.send_msg(topic='/zn/aicamera/gps', msg='N-{},E-{}'.format(latit, longit))
    pub.send_msg(topic='/zn/aicamera/power', msg='power-{}'.format(power))

def dojob(ti,latit,longit,power):
    scheduler = BlockingScheduler()
    # 娣诲姞浠诲姟,鏃堕棿闂撮殧ti MIN
    scheduler.add_job(func, 'interval', minutes=ti, id='job1',args=(latit,longit,power))
    scheduler.start()

while True:
    return_data,shijian,latit, longit = gps_read()
    if (latit != '' and latit != 0) and (longit != '' and longit != 0):
      config['Latit'] = latit
      config['Longit'] = longit
      with open(json_path,'w') as f:
        json.dump(config,f)
      print('xie ru gps success')
      break
    

while True:
    
    # GPS
    return_data,shijian,latit, longit = gps_read()
    print(return_data,shijian,latit, longit)
    # 鍒ゆ柇鏄惁淇″彿
    if latit == '' or latit == 0:
       pub.send_msg(topic='/zn/aicamera/gps',msg='Weak GPS signal')  
    else:
        latit = int(str(latit)[:2])+int(str(latit)[2:])/60
        longit = int(str(longit)[:3])+int(str(latit)[3:])/60
        distance = geodesic((latit, longit), (config['Latit'], config['Longit'])).m
        if distance > config['Distance']:
            pub.send_msg(topic='/zn/aicamera/gps', msg='Displacement occurs')

    # power
    power = power_read()
    #print(power)
    if type(power)==int and power < config['Power']:
       pub.send_msg(topic='/zn/aicamera/power', msg='Low power')

    timer = threading.Thread(target=dojob, args=(5 * 60, latit, longit, power,))
    timer.start()
