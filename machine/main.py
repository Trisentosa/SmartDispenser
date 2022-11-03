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

while True:

    pumpID = 0
    motorID = 0

    #Drink order signal
    orderSignal = db.child("status").child("orderSignal").get().val()
    print("Order Signal")
    print(orderSignal)
    
    #Only retrieve pumpID if user makes a order
    if(orderSignal == True):
        print("Making the order ...")
        rotateMotor()        
        pumpID = int(db.child("currentOrder").child("pumpId").get().val())
        togglePump(pumpID)

    time.sleep(0.5)

cleanup()

# Testing pumps
    # if(get_pump_status() == True):
    #     GPIO.output(0,GPIO.LOW)
    # else:
    #     GPIO.output(0,GPIO.HIGH)
    # time.sleep(0.5)
