#2020.10.04 by mengjun
#V1.2
#send power and gps in fixed time
#add power_low_i 


from apscheduler.schedulers.blocking import BlockingScheduler
from config import Host,Latit,Longit,Distance,Power
from geopy.distance import geodesic
from control.camera_power import gps_read,power_read
from mqtt.publish import Publish
import threading
import json
import time

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

def gps_format_conv(latit,longit):
    latit = int(str(latit)[:2])+float(str(latit)[2:])/60
    longit = int(str(longit)[:3])+float(str(longit)[3:])/60
    return latit,longit
 
#first write gps in congig.json
while True:
    return_data,shijian,latit, longit = gps_read()
    if (latit != '' and latit != 0) and (longit != '' and longit != 0):
      config['Latit'] = latit
      config['Longit'] = longit
      with open(json_path,'w') as f:
        json.dump(config,f)
      print('write gps success')
      break

while True:
    time.sleep(10)
    
    # GPS
    return_data,shijian,latit, longit = gps_read()
    #print('qian:',return_data,latit, longit)
    # 鍒ゆ柇鏄惁淇″彿
    if latit == '' or latit == 0 or len(latit)!= 11 or len(longit)!= 12 :
       pub.send_msg(topic='/zn/aicamera/gps',msg='Weak GPS signal')  
    else:
        latit,longit = gps_format_conv(latit,longit)
        Latit,Longit = gps_format_conv(config['Latit'], config['Longit'])
        #print('latit:',latit,'longit:',longit)
        #print('Latit:',Latit,'Longit:',Longit)
        distance = geodesic((latit, longit), (Latit,Longit)).m
        if distance > config['Distance']:
            pub.send_msg(topic='/zn/aicamera/gps', msg='Displacement occurs')

    # power
    power = power_read()
    #print('power:',power)
    low_power_i = 0
    if type(power)==int and power < config['Power']:
       low_power_i += 1
       if low_power_i > 5:
         pub.send_msg(topic='/zn/aicamera/power', msg='Low power')
     # 60min 
    timer = threading.Thread(target=dojob, args=(1 * 60, latit, longit, power,))
    timer.start()
