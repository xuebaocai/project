#2020.9.07
#用于读取图像是否标记正确

import xml.etree.ElementTree as ET
import os
from lxml import etree
from lxml.etree import Element,SubElement,ElementTree, tostring
from xml.dom.minidom import parseString
import numpy as np
import cv2

def label(srcImgPath,srcXmlPath):
    name = srcImgPath.split('/')[-1]
    fname,pf = name.split('.')

    img = cv2.imread(srcImgPath)
    tree = etree.parse(srcXmlPath)
    root = tree.getroot()
    for obj in root.iter('object'):
        print(obj.find('name').text)
        box = obj.find('bndbox')
        rect = []
        rect.append(int(box.find('xmin').text))
        rect.append(int(box.find('ymin').text))
        rect.append(int(box.find('xmax').text))
        rect.append(int(box.find('ymax').text))
        cv2.rectangle(img,(rect[0],rect[1]),(rect[2],rect[3]),(255,0,0),1)
    cv2.imshow('{}'.format(name),img)
    K = cv2.waitKey(0)
    if K == 27:
        cv2.destroyAllWindows()


def main():
    srcImgPath = 'E:/BaiduNetdiskDownload/models-master/models-master/mydata/data/JPEGImages_aug/'
    srcXmlPath = 'E:/BaiduNetdiskDownload/models-master/models-master/mydata/data/Annotations_aug/'

    files = os.listdir(srcImgPath)
    for f in files:
        fname,pf = f.split('.')
        label(srcImgPath + f,srcXmlPath + fname + '.xml')
    print("done.")

if __name__ == '__main__':
    main()
