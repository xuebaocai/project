import json
import os
from lxml.etree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import time



def make_xml(voc,img_width,img_height,bbox,label,image_name,obj_nums):

    node_root = Element('annotation')

    node_folder = SubElement(node_root, 'folder')
    node_folder.text = voc
    node_filename = SubElement(node_root, 'filename')
    node_filename.text = image_name

    node_size = SubElement(node_root, 'size')
    node_width = SubElement(node_size, 'width')
    node_width.text = str(img_width)
    node_height = SubElement(node_size, 'height')
    node_height.text = str(img_height)
    node_depth = SubElement(node_size, 'depth')
    node_depth.text = '3'

    for i in range(obj_nums):
        node_object = SubElement(node_root, 'object')
        node_name = SubElement(node_object, 'name')
        node_name.text = str(label[i])

        node_difficult = SubElement(node_object, 'difficult')
        node_difficult.text = '0'

        node_bndbox = SubElement(node_object, 'bndbox')
        node_xmin = SubElement(node_bndbox, 'xmin')
        node_xmin.text = str(bbox[i][0])
        node_ymin = SubElement(node_bndbox, 'ymin')
        node_ymin.text = str(bbox[i][1])
        node_xmax = SubElement(node_bndbox, 'xmax')
        node_xmax.text = str(bbox[i][0]+bbox[i][2])
        node_ymax = SubElement(node_bndbox, 'ymax')
        node_ymax.text = str(bbox[i][1]+bbox[i][3])


    xml = tostring(node_root, pretty_print = True)
    dom = parseString(xml)
    #print xml 打印查看结果
    return dom



def bboxs_categorys(img_dir,img_id):
    bboxs = []
    categorys = []

    for ann_i in range(len(anno['annotations'])):
        if anno['annotations'][ann_i]['image_id'] == img_id:
            bbox = anno['annotations'][ann_i]['bbox']
            category = anno['annotations'][ann_i]['category_id']
            bboxs.append(bbox)
            categorys.append(category)
    #print('bboxs', bboxs)
    #print('categorys', categorys)

    return bboxs,categorys


def main(file_name,img_dir,voc):
    with open(file_name, 'r+') as f:
        anno = json.load(f)
    img_nums = len(os.listdir(img_dir))
    for img_id in range (img_nums):
        img_name = anno['images'][img_id]['file_name']
        img_width = anno['images'][img_id]['width']
        img_height = anno['images'][img_id]['height']
        #print(img_id)
        print(img_name)
        bboxs, categorys = bboxs_categorys(img_dir,img_id+1)
        time.sleep(1)

        dom = make_xml(voc, img_width, img_height, bboxs, categorys, img_name, len(categorys))
        xml_name = 'C:/Users/17321/Desktop/project/ann/'+img_name.split('.')[0]+'.xml'
        with open(xml_name, 'wb') as f:
            f.write(dom.toprettyxml(indent='\t', encoding='utf-8'))

if __name__ =='__main__':
    file_name = 'C:/Users/17321/Desktop/DataSet/Dataset/annotations/train.json'
    img_dir = 'C:/Users/17321/Desktop/DataSet/Dataset/train/'
    main(file_name,img_dir,voc='train')
    print('done')