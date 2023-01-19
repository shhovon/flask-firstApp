import numpy as np
import cv2
import datetime as d
import os

def detectObjects(img_path):
    orginal_imgname = os.path.basename(img_path)
    confidenceThreshold = 0.5
    NMSThreshold = 0.3

    modelConfiguration = 'cfg/yolov3.cfg'
    modelWeights = 'yolov3.weights'

    labelsPath = 'coco.names'
    labels = open(labelsPath).read().strip().split('\n')

    np.random.seed(10)
    COLORS = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")

    net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)

    image = cv2.imread(img_path)
    (H, W) = image.shape[:2]


    layerName = net.getLayerNames()
    layerName = [layerName[i - 1] for i in net.getUnconnectedOutLayers()]

    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB = True, crop = False)
    net.setInput(blob)
    #start = time.time()
    layersOutputs = net.forward(layerName)
    #end = time.time()

    #print("[INFO] It took {: 6f} seconds".format(end - start))

    boxes = []
    confidences = []
    classIDs = []

    for output in layersOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > confidenceThreshold:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY,  width, height) = box.astype('int')
                x = int(centerX - (width/2))
                y = int(centerY - (height/2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)


    detectionNMS = cv2.dnn.NMSBoxes(boxes, confidences, confidenceThreshold, NMSThreshold)

    if(len(detectionNMS) > 0):
       for i in detectionNMS.flatten():
           (x, y) = (boxes[i][0], boxes[i][1])
           (w, h) = (boxes[i][2], boxes[i][3])

           color = [int(c) for c in COLORS[classIDs[i]]]
           cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
           text = '{}: {:.4f}'.format(labels[classIDs[i]], confidences[i])
           cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    #cv2.imshow('Image', image)
    #cv2.waitKey(0)
    processed_filename = 'images/processed/processed-'+orginal_imgname
    cv2.imwrite(processed_filename, image)

    outputs= {}
    if len(detectionNMS)>0:
        outputs['detections']={}
        outputs['detections']['labels']=[]
        for i in detectionNMS.flatten():
            detection={}
            detection['Label'] = labels[classIDs[i]]
            #detection['confidence'] = confidences[i]
            detection['X'] = boxes[i][0]
            detection['Y'] = boxes[i][1]
            detection['Width'] = boxes[i][2]
            detection['Height'] = boxes[i][3]
            time = d.datetime.now()
            time = time.strftime("%H:%M:%S- %d-%m-%Y")
            detection['processed_img'] =processed_filename
            detection['Time'] = time
            outputs['detections']['labels'].append(detection)
    else:
        outputs['detections'] = "No objects detected"

    return outputs
