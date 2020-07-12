#-*-coding:gb2312-*-
import numpy as np
from cv2 import cv2 as cv
import os
import time
"""
yolo_dir = '/Users/yunyi/Downloads/yolo3'  # YOLO�ļ�·��
weightsPath = os.path.join(yolo_dir, 'yolov3.weights')  # Ȩ���ļ�
configPath = os.path.join(yolo_dir, 'yolov3.cfg')  # �����ļ�
labelsPath = os.path.join(yolo_dir, 'coco.names')  # label����
"""

dir='/Users/yunyi/Desktop/test'
weightsPath =os.path.join(dir,'yolov3-tiny.weights')   # Ȩ���ļ�
configPath = os.path.join(dir,'yolov3-tiny.cfg') # �����ļ�
labelsPath = os.path.join(dir,'coco.names')  # label����
videoPath=os.path.join(dir,'1.mp4') #��Ƶ·��

#imgPath = '/Users/yunyi/Desktop/tim.jpeg' # ����ͼ��
CONFIDENCE = 0.5  # ������������С����
THRESHOLD = 0.4  # �����ֵ������ֵ

#��ȡ������Ƶ
cap = cv.VideoCapture(videoPath)

#��ȡ����ͷ
#cap = cv.VideoCapture(0)

width=cap.get(3)
height=cap.get(4)
(H, W) = (height,width)
# �������硢����Ȩ��
net = cv.dnn.readNetFromDarknet(configPath, weightsPath)  

# �õ�labels�б�
with open(labelsPath, 'rt') as f:
    labels = f.read().rstrip('\n').split('\n')


# Ӧ�ü����
np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")  # �����ʾ��ɫ��ÿһ���в�ͬ����ɫ��ÿ����ɫ������RGB����ֵ��ɵģ�����sizeΪ(len(labels), 3)
while cap.isOpened():
    ret, frame = cap.read()
    if(ret==True):
        blobImg = cv.dnn.blobFromImage(frame, 1.0/255.0, (416, 416), None, True, False)
        net.setInput(blobImg)  ## ����setInput������ͼƬ���������
        # ��ȡ�����������Ϣ���������������֣����趨��ǰ�򴫲�
        outInfo = net.getUnconnectedOutLayersNames()  ## ǰ���yolov3�ܹ�Ҳ���ˣ�yolo��ÿ��scale���������outInfo��ÿ��scale��������Ϣ����net.forwardʹ��
        # start = time.time()
        layerOutputs = net.forward(outInfo)  # �õ����������ġ������������Ϣ���Ƕ�ά�ṹ��
        # end = time.time()
        # print("[INFO] YOLO took {:.6f} seconds".format(end - start)) ## ���Դ�ӡ����Ϣ


        # �õ�ͼƬ�ߴ�

        # ����layerOutputs
        # layerOutputs�ĵ�1ά��Ԫ������: [center_x, center_y, width, height, objectness, N-class score data]
        # ���˺�Ľ�����룺
        boxes = [] # ���б߽�򣨸�������һ��
        confidences = [] # �������Ŷ�
        classIDs = [] # ���з���ID
        
        # # 1�����˵����Ŷȵ͵Ŀ��
        for out in layerOutputs:  # ���������
            for detection in out:  # �������
                # �õ����Ŷ�
                scores = detection[5:]  # �����������Ŷ�
                classID = np.argmax(scores)  # ������Ŷȵ�id��Ϊ����id
                confidence = scores[classID]  # �õ����Ŷ�
        
                # �������Ŷ�ɸ��
                if confidence > CONFIDENCE:
                    box = detection[0:4] * np.array([W, H, W, H])  # ���߽��Ż�ͼƬ�ߴ�
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
        
        # # 2��Ӧ�÷����ֵ����(non-maxima suppression��nms)��һ��ɸ��
        idxs = cv.dnn.NMSBoxes(boxes, confidences, CONFIDENCE, THRESHOLD) # boxes�У�������box������index����idxs

        if len(idxs) > 0:
            for i in idxs.flatten(): # indxs�Ƕ�ά�ģ���0ά������㣬�����������չƽ��1ά
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
        
                color = [int(c) for c in COLORS[classIDs[i]]]
                cv.rectangle(frame, (x, y), (x+w, y+h), color, 2)  # ������ϸΪ2px
                text = "{}: {:.4f}".format(labels[classIDs[i]], confidences[i])
                cv.putText(frame, text, (x, y-5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)  # cv.FONT_HERSHEY_SIMPLEX������0.5�����С����ϸ2px
        cv.imshow('result', frame)
        cv.waitKey(10)
cap.release()
cv.destroyAllWindows()

