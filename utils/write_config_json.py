import json

my_config = dict({'Mqtt_pub':'183.129.235.180','Mqtt_sub':'183.129.235.180','zone':1,'channel':1,'Latit':30,'Longit':120,
    'Camera_ip':'192.168.8.64','Distance':30,'Power':11500,'Work_time':[['070000'],['240000']],'Is_Polygon':0,'Polygon':[[20,20],[400,20],[400,400],[20,400]]})

json_path = 'config.json'
with open(json_path,'w') as f:
    json.dump(my_config,f)
    
