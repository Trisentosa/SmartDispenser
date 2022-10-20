# trisentosa, meesam, som
# SeniorDesign Project : Smart Dispenser

'''    THIS FILE IS TO BE RUN ON THE RASPBERRY PI
- create a new python file in the root directory of the raspi using "nano test.py"
- copy all the code below and paste it in test.py, now save it
- run the python file from root directory using "python test.py"
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


'''  Button/Switch states  '''
# Using buttons with raspberry pi:  https://gpiozero.readthedocs.io/en/v1.1.0/api_input.html
#                                   https://roboticadiy.com/connect-push-button-with-raspberry-pi-4/
#                                   https://www.rototron.info/using-an-lcd-display-with-inputs-interrupts-on-raspberry-pi/

# pumps
GPIO.setmode(GPIO.BCM)
os.system('modprobe w1-gpio')

pumps = {1:0, 2:5, 3:6, 4:13, 5:19, 6:26}
# Pumps
GPIO.setup(0,GPIO.OUT)  
GPIO.setup(5,GPIO.OUT)  
GPIO.setup(6,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)

motors = {1:17, 2:27}
# # Stepper motor (Boba (mill) dispenser)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)

# # IR/Proximity sensor
GPIO.setup(22,GPIO.OUT)



'''                   Firebase database initialization and sending temperature data                       '''

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

################ NEW CODE ##################

#to-do
# - clean pipe function

timeToFillCup = 8

def get_pump_status(x):
    status = db.child("pumps").child("pump" + str(x)).get().val()
    # time.sleep(0.5)
    return status

def togglePump(x):
    GPIO.output(pumps[x],GPIO.LOW)
    time.sleep(timeToFillCup)

    GPIO.output(pumps[x],GPIO.HIGH)


print(get_pump_status(1))

while True:

    pumpID = 0
    motorID = 0

    #Drink order signal
    orderSignal = db.child("status").child("orderSignal").get().val()
    
    #Only retrieve pumpID if user makes a order
    if(orderSignal == True):
        pumpID = int(db.child("currentOrder").child("pumpId").get().val())
        togglePump(pumpID)





    time.sleep(0.5)








# Testing pumps
    # if(get_pump_status() == True):
    #     GPIO.output(0,GPIO.LOW)
    # else:
    #     GPIO.output(0,GPIO.HIGH)
    # time.sleep(0.5)


