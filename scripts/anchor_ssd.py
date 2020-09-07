#2020.8.31
#用于读取box的长宽比分布

import os
import numpy as np
from sklearn.cluster import KMeans

try:
    import xml.etree.cElementTree as ET  # 解析xml的c语言版的模块
except ImportError:
    import xml.etree.ElementTree as ET
    
##get object annotation bndbox loc start
def GetAnnotBoxLoc(AnotPathDir):  # AnotPath VOC标注文件路径
    dataset = []
    for AnotPath in os.listdir(AnotPathDir):
        #print(AnotPath)
        tree = ET.ElementTree(file=AnotPathDir+AnotPath)  # 打开文件，解析成一棵树型结构
        root = tree.getroot()  # 获取树型结构的根
        ObjectSet = root.findall('object')  # 找到文件中所有含有object关键字的地方，这些地方含有标注目标
        for Object in ObjectSet:
            ObjName = Object.find('name').text
            BndBox = Object.find('bndbox')
            x1 = int(BndBox.find('xmin').text)  # -1 #-1是因为程序是按0作为起始位置的
            y1 = int(BndBox.find('ymin').text)  # -1
            x2 = int(BndBox.find('xmax').text)  # -1
            y2 = int(BndBox.find('ymax').text)  # -1
            dataset.append([(x2 - x1) / (y2 - y1)])
    return np.array(dataset)


if __name__ == '__main__':
    ObjBndBoxSet = GetAnnotBoxLoc("E:/BaiduNetdiskDownload/models-master/models-master/mydata/data/Annotations/")
    #ObjBndBoxSet = GetAnnotBoxLoc("C:/Users/17321/Desktop/VOC2012/VOC2012/Annotations/")
    #print(ObjBndBoxSet)
    kmeans = KMeans(n_clusters=5)
    kmeans.fit(ObjBndBoxSet)
    print(kmeans.cluster_centers_)
