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



'''  Configuring LCD  '''

# lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=36, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)

'''  Button/Switch states  '''
# Using buttons with raspberry pi:  https://gpiozero.readthedocs.io/en/v1.1.0/api_input.html
#                                   https://roboticadiy.com/connect-push-button-with-raspberry-pi-4/
#                                   https://www.rototron.info/using-an-lcd-display-with-inputs-interrupts-on-raspberry-pi/

# # Connect button to GPIO2  
# button = Button(2)
# #buttonState = False

# # Connect switch to GPIO17
# switch = Button(17)
# # switchState = False

# # lED connected to GPIO27
# led = LED(27)

# pumps

pump1 = LED(0)
pump2 = LED(5)
pump3 = LED(6)
pump4 = LED(13)
pump5 = LED(19)
pump6 = LED(26)



# '''                 Connecting to temp sensor and retrieving data                   '''

# Start/Initialize the GPIO Pins
os.system('modprobe w1-gpio')  # Turns on the GPIO module
# os.system('modprobe w1-therm') # Turns on the Temperature module

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


# def sendSms(toNumber):
#     '''Takes phone number as arg to the function and sends extreme temperatures sms notification to that phone number'''

#     account_sid = 'ACc948439e80f605cc32693f38bc027052' 
#     auth_token = '7273f38197d03626837d4e818f2dd8ab'
#     client = Client(account_sid, auth_token) 
    
#     if highTemp():
#         client.messages.create(  
#                                 messaging_service_sid='MG1d68b0889c53c0e566a20d215b56b359',       
#                                 to=str(toNumber),
#                                 body= "High temperature reached: " + read_temp_c() + "°" + "C" + " / " + read_temp_f() + "°" + "F" )
#     elif lowTemp():
#         client.messages.create(  
#                                 messaging_service_sid='MG1d68b0889c53c0e566a20d215b56b359',       
#                                 to=str(toNumber),
#                                 body= "Low temperature reached: " + read_temp_c() + "°" + "C" + " / " + read_temp_f() + "°" + "F"             
                                 
#                         ) 

# Main while loop
while True:
    pump1.on
        


GPIO.cleanup() # cleanup all GPIO
lcd.clear()







# if button.is_pressed or (db.child("Status").child("VirtualButton").get().val() == "True") :
    #     lcd.cursor_pos = (0, 0)    
    #     lcd.write_string("Temp: " + read_temp_c() + chr(223) + "C")
    #     lcd.cursor_pos = (1, 0)
    #     lcd.write_string("Temp: " + read_temp_f() + chr(223) + "F")

    #     stateIO = {
    #         "Button" : "True"
    #         #"Switch" : switchState
    #     }

    # else:
    #     lcd.clear()
        
    #     lcd_display.backlight_enabled = False

    #     stateIO = {
    #         "Button" : "False"
    #         #"Switch" : switchState
    #     }

    # db.child("States").set(stateIO)


    # # firbase method send temp_C to firebase 
    # temperatureData = {
    #     "TempC": read_temp_c(),
    #     "TempF": read_temp_f(), 
    #     "Time" : time.time()
    # }

    # db.child("Temperatures").set(temperatureData)


    # print(db.child("Temperatures").child("TempC").get().val() )