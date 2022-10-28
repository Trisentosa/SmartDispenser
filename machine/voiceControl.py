import speech_recognition as sr
import pyttsx3
import pyrebase
import time 
#machine state:
# 0: wait for someone to speak
# 1: wait for order signal

# FIREBASE CONFIG AND INITIALIZATION
config = {
  "apiKey": "AIzaSyBY8DyNfV_B2NSlKHr4sZRvRT1fBMlOuwQ",
  "authDomain": "smartdispenser-ac92a.firebaseapp.com",
  "databaseURL": "https://smartdispenser-ac92a-default-rtdb.firebaseio.com",
  "projectId": "smartdispenser-ac92a",
  "storageBucket": "smartdispenser-ac92a.appspot.com",
  "messagingSenderId": "669426580100",
  "appId": "1:669426580100:web:b0c2df77a34e687a33e0d1",
  "measurementId": "G-P7WDJV5GDK"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()


#speech recognition initialization
recognizer = sr.Recognizer()
state = 0

#get drink name from firebase
words = {}
drinkSettings = db.child("maintainer").child("drinkSetting").get().val()
for key,value in drinkSettings.items():
    drinkName = value["name"].lower().replace(" ", "")
    drinkNumber = key[-1] # key : drink<x> where x is drink number
    words[drinkNumber] = drinkName

#MAIN LOOP
while True:
    #STATE 0: LISTEN
    #note : while voice signal is false check?s
    if state == 0:
        try:
            with sr.Microphone() as mic:
                #Listen for text
                print("listening")
                audio = recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recognizer.listen(mic)

                text = recognizer.recognize_google(audio)
                print("original text: ",text)
                text = text.lower().replace(" ", "")
                print("parsed text: ",text)

                #Parse text and find in words list
                found = False
                i = 1 # drink number, starts at 1
                for drinkNumber, drinkName in words.items():
                    if drinkName in text and not found:
                        state = 1
                        found = True
                        print("found :",drinkName)
                        # set voice signal in firebase and drinkNumber
                        # Once read by the website, from website set the signal false
                        db.child("voiceSignal").child("isSet").set(True)   
                        db.child("voiceSignal").child("drinkNumber").set(drinkNumber)          

        #reinitialize if error
        except sr.UnknownValueError:
            recognizer = sr.Recognizer()
            continue
    #STATE 1: WAIT ORDER SIGNAL
    else:
        print("In state 1, waiting for order signal")
        # db.child("voiceSignal").child("isSet").set(False)
        # state = 0 # replace this line with main.py code



