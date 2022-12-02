'''    SMART DISPENSER - Team Kiwi
- Team Members: Meesam, Som, Tri
- This file is responsible for controlling the main logic of the machine, as well as 
- controlling the pumps, stepper motor, proximity sensor, and voice control input
'''

import os
import glob
import time
import datetime
import RPi.GPIO as GPIO
from RPLCD import CharLCD
from gpiozero import Button, LED    # https://gpiozero.readthedocs.io/en/stable/index.html
import pyrebase
from twilio.rest import Client
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
from playsound import playsound

time.sleep(45)
'''                   Voice Control Setup                       '''
recognizer = sr.Recognizer()

# return a dict where key:drinkNumber -> value: drinkName
def getWords():
    words = {}
    drinkSettings = db.child("maintainer").child("drinkSetting").get().val()
    for key,value in drinkSettings.items():
        drinkName = value["name"].lower().replace(" ", "")
        drinkNumber = key[-1] # key : drink<x> where x is drink number
        words[drinkNumber] = drinkName
    return words

'''                   GPIO and components setup                        '''

# GPIO setup
GPIO.setmode(GPIO.BCM)
#os.system('modprobe w1-gpio')

# Pumps
pumps = {1:0, 2:5, 3:6, 4:13, 5:19, 6:26}

GPIO.setup(0,GPIO.OUT)  
GPIO.setup(5,GPIO.OUT)  
GPIO.setup(6,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)

# # Stepper motor (Boba (mill) dispenser)
in1 = 17
in2 = 18
in3 = 27
in4 = 22
 
# lower -> faster turn speed. lowest is around 0.002
step_sleep = 0.003
 
step_count = 4096 # 5.625*(1/64) per step, 4096 steps is 360°, 4096 = 1 rotation
 
# defining stepper motor sequence
step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]]
 
# motor setting up
GPIO.setmode( GPIO.BCM )
GPIO.setup( in1, GPIO.OUT )
GPIO.setup( in2, GPIO.OUT )
GPIO.setup( in3, GPIO.OUT )
GPIO.setup( in4, GPIO.OUT )
 
# initializing
GPIO.output( in1, GPIO.LOW )
GPIO.output( in2, GPIO.LOW )
GPIO.output( in3, GPIO.LOW )
GPIO.output( in4, GPIO.LOW )

motor_pins = [in1,in2,in3,in4]
motor_step_counter = 0 
 
def cleanup():
    GPIO.output( in1, GPIO.LOW )
    GPIO.output( in2, GPIO.LOW )
    GPIO.output( in3, GPIO.LOW )
    GPIO.output( in4, GPIO.LOW )
    GPIO.cleanup()

# # IR/Proximity sensor
#GPIO.setup(22,GPIO.OUT)

'''                   Firebase database initialization                        '''

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

'''                   Functions for Making Order                        '''

#to-do
# - clean pipe function

#time to fill the cup in seconds
timeToFillCup = 15

def get_pump_status(x):
    status = db.child("pumps").child("pump" + str(x)).get().val()
    # time.sleep(0.5)
    return status

def togglePump(x):
    GPIO.output(pumps[x],GPIO.LOW)
    time.sleep(timeToFillCup)
    GPIO.output(pumps[x],GPIO.HIGH)
    db.child("status").child("orderSignal").set(False)

def rotateMotor():
    i = 0
    motor_step_counter = 0
    for i in range(step_count):
        for pin in range(0, len(motor_pins)):
            GPIO.output( motor_pins[pin], step_sequence[motor_step_counter][pin] )
        motor_step_counter = (motor_step_counter - 1) % 8 # clockwise, cc +1 instead
        time.sleep( step_sleep )

#voice assistant
db.child("voiceAssistant").child("voiceState").set(0) #init voice state to 0
db.child("voiceAssistant").child("sayIt").set(True) #init sayIt True
voiceDict = {0:"welcome.mp3",1:"orderComplete.mp3",2:"paymentComplete.mp3",3:"makingOrder.mp3",4:"orderDone.mp3"}
def voiceAssistant():
    assistantData = db.child("voiceAssistant").get().val()
    isActive = db.child("voiceAssistant").child("isActive").get().val()
    sayIt = db.child("voiceAssistant").child("sayIt").get().val()
    voiceState = assistantData["voiceState"]
    if isActive and sayIt:
        playsound('audio/{}'.format(voiceDict[voiceState]))
        db.child("voiceAssistant").child("sayIt").set(False)

'''                   MAIN LOOP                       '''
print("MACHINE IS STARTING")
db.child("status").child("test").set(60)
while True:
    db.child("status").child("test").set(30)
    pumpID = 0
    motorID = 0
    state = db.child("status").child("state").get().val()

    voiceAssistant()

    # LISTENING FOR VOICE STATE (0)
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
                words = getWords()
                for drinkNumber, drinkName in words.items():
                    if drinkName in text and not found:
                        db.child("status").child("state").set(1)
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

    # WAITING FOR ORDER STATE (1)
    else:
        print("In state 1, waiting for order signal...")

        #Drink order signal
        orderSignal = db.child("status").child("orderSignal").get().val()
        print("Order Signal")
        print(orderSignal)
        
        #Only retrieve pumpID if user makes a order
        if(orderSignal == True):
            print("Making the order ...")
            #voice assistant set voiceState 3
            db.child("voiceAssistant").child("voiceState").set(3)
            db.child("voiceAssistant").child("sayIt").set(True)
            #Order making
            addTopping = db.child("currentOrder").child("addTopping").get().val()
            if(addTopping):
                rotateMotor()        
            pumpID = int(db.child("currentOrder").child("pumpId").get().val())
            togglePump(pumpID)
            db.child("status").child("state").set(0)
            #voice assistant set voiceState 3
            db.child("voiceAssistant").child("voiceState").set(4)
            db.child("voiceAssistant").child("sayIt").set(True)

        time.sleep(0.5)

cleanup()
