from apscheduler.schedulers.blocking import BlockingScheduler
from config import Host,Latit,Longit,Distance,Power
from geopy.distance import geodesic
from control.camera_power import gps_read,power_read
from mqtt.publish import Publish
from config import Host
import threading


pub = Publish(host=Host)

def func(latit,longit,power):
    pub.send_msg(topic='/zn/aicamera/gps', msg='N-{},E-{}'.format(latit, longit))
    pub.send_msg(topic='/zn/aicamera/power', msg='power-{}'.format(power))

def dojob(ti,latit,longit,power):
    scheduler = BlockingScheduler()
    # 添加任务,时间间隔ti MIN
    scheduler.add_job(func, 'interval', minutes=ti, id='job1',args=(latit,longit,power))
    scheduler.start()

while True:
    # GPS
    latit, longit = gps_read()
    # 判断是否信号
    if latit == '' or latit == 0:
       pub.send_msg(topic='/zn/aicamera/gps',msg='Weak GPS signal')
    # 如果有判断移位距离
    else:
        print(latit)
        latit = int(str(latit)[:2])+int(str(latit)[2:])/60
        longit = int(str(longit)[:3])+int(str(latit)[3:])/60
        distance = geodesic((latit, longit), (Latit, Longit)).m
        if distance > Distance:
            pub.send_msg(topic='/zn/aicamera/gps', msg='Displacement occurs')

    # power
    power = power_read()
    #print(power)
    if type(power)==int and power < int(Power):
       pub.send_msg(topic='/zn/aicamera/power', msg='Low power')

    timer = threading.Thread(target=dojob, args=(5 * 60, latit, longit, power,))
    timer.start()
