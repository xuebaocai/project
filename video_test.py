#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np

class general_yolov3(object):
    def __init__(self):
        self.conf_threshold = 0.5  # Confidence threshold
        self.nms_threshold = 0.4  # NMS threshold
        self.net_width = 416  # 网络输入图像宽度
        self.net_height = 416  # 网络输入图像高度
        self.classes = self.get_coco_names()
        self.yolov3_model = self.get_yolov3_model()
        self.outputs_names = self.get_outputs_names()

    def get_coco_names(self):
        classesFile = "obj.names"
        classes = None
        with open(classesFile, 'rt') as f:
            classes = f.read().rstrip('\n').split('\n')
        return classes

    def get_yolov3_model(self):
        cfg_file =  "yolov3-tiny.cfg"
        weights_file =  "yolov3-tiny_10000.weights"

        net = cv2.dnn.readNetFromDarknet(cfg_file, weights_file)
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        return net

    def get_outputs_names(self):
        # 所有网络层名
        layersNames = self.yolov3_model.getLayerNames()
        # 输出网络层名，如无连接输出的网络层.
        return [layersNames[i[0] - 1] for i in
                self.yolov3_model.getUnconnectedOutLayers()]

    def postprocess(self, img_cv2, outputs):
        # 检测结果后处理
        # 采用 NMS 移除低 confidence 的边界框
        img_height, img_width, _ = img_cv2.shape

        # 只保留高 confidence scores 的输出边界框
        # 将最高 score 的类别标签作为边界框的类别标签
        class_ids = []
        confidences = []
        boxes = []
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.conf_threshold:
                    center_x = int(detection[0] * img_width)
                    center_y = int(detection[1] * img_height)
                    width = int(detection[2] * img_width)
                    height = int(detection[3] * img_height)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        # NMS 处理， 消除 lower confidences 的冗余重叠边界框
        indices = cv2.dnn.NMSBoxes(boxes,
                                   confidences,
                                   self.conf_threshold,
                                   self.nms_threshold)
        results = []
        for ind in indices:
            res_box = {}
            res_box["class_id"] = class_ids[ind[0]]
            res_box["score"] = confidences[ind[0]]

            box = boxes[ind[0]]
            res_box["box"] = (box[0],
                              box[1],
                              box[0] + box[2],
                              box[1] + box[3])
            results.append(res_box)
        return results

    def predict(self, img_cv2):
        # 创建网络输入的 4D blob.
        blob = cv2.dnn.blobFromImage(
            img_cv2, 1 / 255,
            (self.net_width, self.net_height),
            [0, 0, 0], 1, crop=False)
        # 设置模型的输入 blob
        self.yolov3_model.setInput(blob)
        # 前向计算
        outputs = self.yolov3_model.forward(self.outputs_names)
        # 后处理
        results = self.postprocess(img_cv2, outputs)
        return results

    def vis_res(self, img_cv2, results):
        # 可视化检测结果
        for result in results:
            left, top, right, bottom = result["box"]
            cv2.rectangle(img_cv2,
                          (left, top),
                          (right, bottom),
                          (255, 178, 50), 3)

            # 边界框的类别名和 confidence score
            label = '%.2f' % result["score"]
            class_id = result["class_id"]
            if self.classes:
                assert (result["class_id"] < len(self.classes))
                label = '%s:%s' % (self.classes[class_id], label)
            #
            label_size, baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            top = max(top, label_size[1])
            cv2.rectangle(
                img_cv2,
                (left, top - round(1.5 * label_size[1])),
                (left + round(1.5 * label_size[0]),
                 top + baseline), (255, 0, 0),
                cv2.FILLED)
            cv2.putText(img_cv2, label, (left, top),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 0, 0), 1)

        # 计算速率信息
        # getPerfProfile() 函数返回模型的推断总时间以及
        # 每一网络层的耗时(in layersTimes).
        t, _ = self.yolov3_model.getPerfProfile()
        label = 'Inference time: %.2f ms' % \
                (t * 1000.0 / cv2.getTickFrequency())
        cv2.putText(img_cv2, label, (0, 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
        cv2.imshow('frame',img_cv2)
        cv2.waitKey(1)

if __name__ == '__main__':
    print("[INFO]Yolov3 object detection in OpenCV.")
    cap = cv2.VideoCapture(0)
    print(cap.isOpened())
    while(cap.isOpened()):
        ret,frame = cap.read()
        yolov3_model = general_yolov3()
        results = yolov3_model.predict(frame)
        yolov3_model.vis_res(frame, results)
    cap.release()
    cv2.destroyAllWindows()
