from apscheduler.schedulers.blocking import BlockingScheduler
from geopy.distance import geodesic
from control.camera_power import gps_read, power_read
from mqtt.publish import Publish
from utils.mem import getMEM, getCPU
import threading
import json
import time

json_path = '/home/mengjun/xianlu/tensorrt_demos/utils/config.json'
with open(json_path, 'r') as f:
    config = json.load(f)

# print(config)

pub = Publish(host=config['Mqtt_pub'])


def func(latit, longit, power, mem, cpu):
    print('send')
    pub.send_msg(topic='/zn/aicamera/{}/{}/gps'.format(config['zone'], config['channel']),
                 msg='N-{},E-{},time-{}'.format(latit, longit,time.ctime()))
    pub.send_msg(topic='/zn/aicamera/{}/{}/status'.format(config['zone'], config['channel']),
                 msg='power-{},mem-{},cpu-{},time-{}'.format(power, mem, cpu,time.ctime()))


def dojob(ti, latit, longit, power, mem, cpu):
    scheduler = BlockingScheduler()
    # 添加任务,时间间隔ti MIN
    scheduler.add_job(func, 'interval', minutes=ti, id='job1', args=(latit, longit, power, mem, cpu))
    scheduler.start()


def gps_format_conv(latit, longit):
    latit = int(str(latit)[:2]) + float(str(latit)[2:]) / 60
    longit = int(str(longit)[:3]) + float(str(longit)[3:]) / 60
    return latit, longit

while True:
    return_data, shijian, latit, longit = gps_read()
    if (latit != '' and latit != 0) and (longit != '' and longit != 0):
        config['Latit'] = latit
        config['Longit'] = longit
        with open(json_path, 'w') as f:
            json.dump(config, f)
        print('xie ru gps success')
        break

while True:
    time.sleep(10)
    
    # mem ,cpu
    mem = getMEM()
    cpu = getCPU()
    # GPS
    return_data, shijian, latit, longit = gps_read()
    # print('qian:',return_data,latit, longit)
    # 判断是否信号
    if latit == '' or latit == 0 or len(latit) != 11 or len(longit) != 12:
        pub.send_msg(topic='/zn/aicamera/{}/{}/gps'.format(config['zone'], config['channel']),
                     msg='Weak GPS signal,time-{}'.format(time.ctime()))
    else:
        latit, longit = gps_format_conv(latit, longit)
        Latit, Longit = gps_format_conv(config['Latit'], config['Longit'])
        print('latit:', latit, 'longit:', longit)
        print('Latit:', Latit, 'Longit:', Longit)
        distance = geodesic((latit, longit), (Latit, Longit)).m
        if distance > config['Distance']:
            pub.send_msg(
                topic='/zn/aicamera/{}/{}/gps'.format(config['zone'], config['channel']),
                msg='Displacement occurs,time-{}'.format(time.ctime()))

        # power
    power = power_read()
    # print('power:',power)
    low_power_i = 0
    if type(power) == int and power < config['Power']:
        low_power_i += 1
    if low_power_i > 7:
        pub.send_msg(topic='/zn/aicamera/{}/{}/status'.format(config['zone'], config['channel']),
                     msg='Low power,time-{}'.format(time.ctime()))

    if cpu >= 99:
        pub.send_msg(topic='/zn/aicamera/{}/{}/status'.format(config['zone'], config['channel']),
                     msg='high cpu,time-{}'.format(time.ctime()))

    timer = threading.Thread(target=dojob, args=(1, latit, longit, power, mem, cpu,))
    timer.start()
