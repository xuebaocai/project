import os
import numpy as np
import cv2 as cv
import json
from skimage import draw


output_path = "C:/Users/admin/Desktop/pipeline/pipeline/mask_img/"
root_dir = 'C:/Users/admin/Desktop/pipeline/pipeline/'

annotations = json.load(open(root_dir+'via_project_15Jul2021_16h35m.json',encoding='utf-8'))  # 加载json文件
annotations = list(annotations.values())
annotations_point = annotations[1]
annotations_point = list(annotations_point.values())

annotations_point = [a for a in annotations_point if a['regions']]

num = 0
for i in range(len(annotations_point)): 

    filename = annotations_point[i]['filename']
    try:
        if filename.startswith('微信'):
            filename = filename.replace(filename.split('_')[0], 'weixin')
        print(root_dir+'data/'+filename.replace('jpeg','jpg'))
        image = cv.imread(root_dir+'data/'+filename.replace('jpeg','jpg'))

        height, width = image.shape[:2]
        #print('height, width',height, width)
        mask = np.zeros([height, width], dtype=np.uint8) 
        for j in range(len(annotations_point[i]['regions'])):  
           
            point = annotations_point[i]['regions'][j]['shape_attributes']
            point_x = point['all_points_x']  # 提取x点数据
            point_y = point['all_points_y']  # 提取y点数据
            if height in point_y:
                index = point_y.index(height)
                point_y[index] -= 1

            if width in point_x:
                index = point_x.index(width)
                point_x[index] -= 1


            rr, cc = draw.polygon(point_y, point_x) 
            #print('rr, cc',rr, cc)
            mask[rr, cc] = 1  # one class
        #cv.imshow("mask_"+filename,mask)
        #cv.waitKey(0)
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        cv.imwrite(output_path + filename.replace('jpeg','png'), mask)  
    except:
        num +=1
        print(num)
