import xml.etree.ElementTree as ET
import os
from lxml import etree
from lxml.etree import Element,SubElement,ElementTree, tostring
from xml.dom.minidom import parseString
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import time

def label(srcImgPath,srcXmlPath):


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
        cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (255, 0, 0), 1)

    cv2.imshow('{}'.format(srcImgPath),img)


    K = cv2.waitKey(0)
    if K == 27:
        cv2.destroyAllWindows()


def main():
    srcImgPath = 'C:/Users/17321/Desktop/DataSet/Dataset/train/'
    srcXmlPath = 'C:/Users/17321/Desktop/project/ann/'

    for ann_i in os.listdir(srcXmlPath):
        fname = ann_i.split('.')[0]
        label(srcImgPath + fname + '.jpg' ,srcXmlPath + ann_i)
    print("done.")

if __name__ == '__main__':
    main()