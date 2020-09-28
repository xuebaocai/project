import json

my_config = dict({'Mqtt_pub':'192.168.8.101','Mqtt_sub':'192.168.8.101','Latit':30,'Longit':120,
    'Camera_ip':'192.168.8.64','Distance':30,'Power':11500,'Work_time':'[0700,1800]','Polygon':[]})

json_path = 'config.json'
with open(json_path,'w') as f:
    json.dump(my_config,f)

