import pyrebase
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

# pump1_status = db.child("pumps").child("pump1").get().val()
# pump2_status = db.child("pumps").child("pump2").get().val()
# pump3_status = db.child("pumps").child("pump3").get().val()
# pump4_status = db.child("pumps").child("pump4").get().val()
# pump5_status = db.child("pumps").child("pump5").get().val()
# pump6_status = db.child("pumps").child("pump6").get().val()

# print(pump1_status)

def get_pump1_status():
    status = db.child("pumps").child("pump1").get().val()
    return status
    
def get_pump2_status():
    status = db.child("pumps").child("pump2").get().val()
    return status

def get_pump3_status():
    status = db.child("pumps").child("pump3").get().val()
    return status

def get_pump4_status():
    status = db.child("pumps").child("pump4").get().val()
    return status

def get_pump5_status():
    status = db.child("pumps").child("pump5").get().val()
    return status

def get_pump6_status():
    status = db.child("pumps").child("pump6").get().val()
    return status


print(get_pump1_status())
print(get_pump2_status())
print(get_pump3_status())
print(get_pump4_status())
print(get_pump5_status())
print(get_pump6_status())


# def pump1_toggleON():
#     if get_pump1_status == "False":
#         GPIO.output(0,GPIO.LOW)
#         # time.sleep(2)
#     else: 
#         GPIO.output(0,GPIO.HIGH)


    



# if pump1_status == "True":
#     GPIO.output(0,GPIO.LOW)
#     time.sleep(2)
        
