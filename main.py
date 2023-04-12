import cv2
import pyttsx3
import time

##OPENCV DNN
net = cv2.dnn.readNet("E:/Project/new/dnn_model/yolov4-tiny.weights", "E:/Project/new/dnn_model/yolov4-tiny.cfg")
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size =(320,320), scale = 1/255)

##INITIALISING SPEECH LIBRARY
text_speech=pyttsx3.init()


## LOAD CLASS LISTS
classes = []  ##empty list of python
file_name = "E:/Project/new/dnn_model/classes.txt"

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

l=list()
while True:
    ## GET FRAMES
    ret,frame = cap.read()

    ##OBJECT DETECTION
    (class_ids, scores, bboxes)= model.detect(frame)
    l.clear()
    for class_id, score, bbox in zip(class_ids, scores, bboxes):
        #print("First : ",l)
        #l.clear()
        print("Second")
        if(score>0.5):
            (x,y,w,h) = bbox
            class_name = classes[class_id]
            l.append(class_name)

            cv2.putText(frame, class_name, (x, y-10), font, fontScale= font_scale, color = (200, 0, 50), thickness= 2)
            cv2.rectangle(frame, (x,y),(x+w, y+h), (200, 0, 50), 3)

    l=[*set(l)]
    if(len(l)!=0):
        res1=','.join(l)
        res2=f"You have {res1} in front of you."
    else:
        res2="You have nothing in front of you."
    text_speech.say(res2)
    text_speech.runAndWait()
    print("class id", class_ids," and ",l)
    time.sleep(5)
    #print("scores", scores)
    #print("bboxes", bboxes)

    #cv2.imshow("Frame", frame)
    #cv2.waitKey(1)