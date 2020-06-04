#! /bin/bash

uri="rtsp://admin:adm182333@192.168.1.64:554"
log_path=/home/mengjun/log.txt

if [ -e ${log_path} ]; then
	rm ${log_path}
fi

cd /home/mengjun/project/control

sudo python3 camera_power.py --up

if [ $? -eq 0 ] ;then
	echo "camera_power:up" >> ${log_path}
	sleep 40
	python3 /home/mengjun/project/tensorrt_demos/trt_ssd.py --rtsp --uri ${uri}

	if [ $? -eq 0 ] ;then
		echo "camera_decetion:up" >> ${log_path}
	else
		echo "camer_decetion:error" >> ${log_path}
		exit
	fi
else
	echo "camer_power:up error" >> ${log_path}
fi

