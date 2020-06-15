import hiai
from atlasutil import ai
import cv2 as cv
import numpy as np
import os
import time

resize_w = 300
resize_h = 300

model_path = './model/deploy.om'
mp4 = ''
CLASSES = ("background","person","hat","digger","truck")

def main():
    if not os.path.exists(mp4):
        print("mp4 not exists, please check: %s" % mp4)

    cap = cv.VideoCapture(mp4)
    my_graph = ai.Graph(model_path)

    while True:
        success, bgr_img = cap.read()
        if bgr_img is None:
            break
        img = cv.resize(bgr_img, (resize_w, resize_h))
        print("start")

        #推理结果
        result_list = my_graph.Inference(img)
        if not result_list:
            print("get no result")
            return

        h, w = bgr_img.shape[0], bgr_img.shape[1]
        solution = (h, w)

        # 后处理
        detection_result_list = ai.SSDPostProcess(result_list, solution, 0.5, CLASSES)
        for result in detection_result_list:
            cv.rectangle(bgr_img, (result.lt.x,result.lt.y) , (result.rb.x, result.rb.y), (0,255,0))
            p3 = (max(result.lt.x, 15), max(result.lt.y, 15))
            cv.putText(bgr_img, result.result_text, p3, cv.FONT_ITALIC, 0.6, (0, 255, 0), 1)
            print(result.result_text)

    print("over")

if __name__ == '__main__':
    main()
