import cv2
import pyttsx3
import time
import requests
import os
import speech_recognition as sr
import key

# generate voice instructions
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # change voice here if needed

def object_detection():
    try:
        ##OPENCV DNN
        if(os.path.isdir("dnn_model")):
            os.chdir("dnn_model")
            dir="dnn_model"
            f1="yolov4.weights"
            f2="yolov4.cfg"
            f3="classes.txt"
            weights=os.path.abspath(f1)
            config=os.path.abspath(f2)
            file_name=os.path.abspath(f3)
        else:
            print("Required Files Not Found.")
            return
        os.chdir("..")
        net = cv2.dnn.readNet(weights, config)
        model = cv2.dnn_DetectionModel(net)
        model.setInputParams(size =(320,320), scale = 1/255)

        ## LOAD CLASS LISTS
        classes = []

        with open(file_name, "rt") as f:
            for class_name in f.readlines():
                class_name = class_name.strip()
                classes.append(class_name)

        ## INITIALIZE CAMERA
        cap = cv2.VideoCapture(0)

        objects=list()
        while True:
            ## GET FRAMES
            ret,frame = cap.read()

            ##OBJECT DETECTION
            (class_ids, scores, bboxes)= model.detect(frame)
            objects.clear()
            for class_id, score, bbox in zip(class_ids, scores, bboxes):
                if(score>0.6):
                    class_name = classes[class_id]       #Object names
                    objects.append(class_name)

            objects=[*set(objects)]
            if(len(objects)!=0):
                res1='and'.join(objects)
                res2=f"You have {res1} in front of you."
            else:
                res2="You have nothing in front of you."
            engine.say(res2)
            engine.runAndWait()                             #Stops the program until the text-to-speech synthesis is completed
            
            print("class id", class_ids," and ",objects)
            time.sleep(2)
    except KeyboardInterrupt:
        return



def navigation(API_KEY,origin,destination):
    # calculate the directions from point A to point B using Google Maps API
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={API_KEY}"
    response = requests.get(url)
    data = response.json()


    for i,step in enumerate(data['routes'][0]['legs'][0]['steps']):
        try:
            instruction = step["html_instructions"]
            instruction = instruction.replace('<b>', '').replace('</b>', '') # remove bold tags
            instruction = instruction.replace('<div style="font-size:0.9em">', '').replace('</div>', '') # remove div tags
            instruction = instruction.replace('<div style="font-size:0.9em; padding-left:1em">', '').replace('</div>', '') # remove div tags
            instruction = instruction.replace('<br/>', ' ') # replace line breaks with spaces
            instruction = instruction.replace('&nbsp;', '') # remove non-breaking spaces
            instruction = instruction.replace('&amp;', 'and') # remove ampersand
            instruction = instruction.replace('Rd', 'Road') # Rd->Road
            instruction = instruction.replace('Ln', 'Lane') # Ln->Lane
            instruction = instruction.replace('/<wbr/>', 'and then') # remove word-break tags
            instruction = instruction.strip() # remove leading/trailing whitespace
            print(f"{i+1}. {instruction}")
            engine.say(instruction)
            engine.runAndWait()
            object_detection()
        except KeyboardInterrupt:
            return



def landmarks(API_KEY,origin):
    try:
        # Ask user for address input
        choice = int(input("Enter choice number : "))
        choice -=1 
        list = ["atm","bank","doctor","hospital","pharmacy","school","police"]

        # Define API endpoint and parameters
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": None,
            "radius": 1000,
            "type": list[choice],
            "key": API_KEY
        }

        # Use Geocoding API to get latitude and longitude of user address
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {"address": origin, "key": API_KEY}
        response = requests.get(geocode_url, params=geocode_params)
        json = response.json()
        location = json["results"][0]["geometry"]["location"]
        params["location"] = f"{location['lat']},{location['lng']}"

        # Use Places API to search for nearby hospitals
        response = requests.get(url, params=params)
        json = response.json()
        landmarks = json["results"]

        # Add hospital markers to map
        for landmark in landmarks:
            name = landmark["name"]
            print(name)
            engine.say(f"Do you want to go to {name}?")
            engine.runAndWait()
            n = int(input("Enter : \n1 for 'Yes'\n2 for 'No'\n"))
            if(n==1):
                name1=str(landmark["geometry"]["location"]["lat"])+","+str(landmark["geometry"]["location"]["lng"])
                navigation(API_KEY,origin,name1)
            elif(n==2):
                continue
            else:
                engine.say("Invalid Choice.")
                engine.runAndWait()
                break
    except KeyboardInterrupt:
        return



if __name__ == "__main__":
    API_KEY=key.api_key

    key = int(input("What do you want to do? \n1. Obstacle Detection \n2. Navigation \n3. Nearest Landmarks\n"))
    if(key==1): 
        object_detection()
    elif(key==2):
        q=int(input("Enter \n1 for 'manual input'\n2 for 'audio input'\n"))
        if(q==2):
            # recognize origin and destination using speech
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Say your origin location!")
                audio = r.listen(source)

            try:
                origin = r.recognize_google(audio)
                print("You said: " + origin)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                origin = ""

            with sr.Microphone() as source:
                print("Say your destination location!")
                audio = r.listen(source)

            try:
                destination = r.recognize_google(audio)
                print("You said: " + destination)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service {0}".format(e))
                destination = ""
            navigation(API_KEY,origin,destination)
        elif(q==1):
            origin=input("Enter origin : ")
            destination=input("Enter destination : ")
            navigation(API_KEY,origin,destination)
        else:
            print("Invalid Choice. Please retry again.")
    
    elif(key==3):
        q=int(input("Enter \n1 for 'manual input'\n2 for 'audio input'\n"))
        if(q==2):
            # recognize origin using speech
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Say your origin location!")
                audio = r.listen(source)

            try:
                origin = r.recognize_google(audio)
                print("You said: " + origin)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                origin = ""
            landmarks(API_KEY,origin)
        elif(q==1):
            origin=input("Enter origin : ")
            landmarks(API_KEY,origin)
        else:
            print("Invalid Choice. Please retry again.")        
    else:
        print("Invalid Choice. Please try again.")