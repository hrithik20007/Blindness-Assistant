import cv2

##OPENCV DNN
net = cv2.dnn.readNet("E:/Project/BAS-OPENCVn/dnn_model/yolov4-tiny.weights", "E:/Project/BAS-OPENCVn/dnn_model/yolov4-tiny.cfg")
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size =(320,320), scale = 1/255)

## LOAD CLASS LISTS
classes = []  ##empty list of python
file_name = "E:/Project/BAS-OPENCVn/dnn_model/classes.txt"

with open(file_name, "rt") as fpt:
    for class_name in fpt.readlines():
        class_name = class_name.strip()
        classes.append(class_name)

## INITIALIZE CAMERA
cap = cv2.VideoCapture(0)

## CHANGING VIDEO FEED RESOLUTION
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

font_scale = 3
font = cv2.FONT_HERSHEY_PLAIN

while True:
    ## GET FRAMES
    ret,frame = cap.read()

    ##OBJECT DETECTION
    (class_ids, scores, bboxes)= model.detect(frame)
    for class_id, score, bbox in zip(class_ids, scores, bboxes):
        (x,y,w,h) = bbox
        class_name = classes[class_id]

        cv2.putText(frame, class_name, (x, y-10), font, fontScale= font_scale, color = (200, 0, 50), thickness= 2)
        cv2.rectangle(frame, (x,y),(x+w, y+h), (200, 0, 50), 3)


    print("class id", class_ids)
    print("scores", scores)
    print("bboxes", bboxes)

    cv2.imshow("Frame", frame)
    cv2.waitKey(1)