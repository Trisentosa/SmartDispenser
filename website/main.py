from flask import Flask, render_template, flash, session, request, redirect, url_for, make_response, Response
import requests
import os
from requests.auth import HTTPBasicAuth
import pyrebase
import json
import payment
import bcrypt
import uuid
from dotenv import load_dotenv

#ENV Variables
load_dotenv()
FIREBASE_KEY = os.getenv("FIREBASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
# encrypts cookies and session data related to website
app.config['SECRET_KEY'] = SECRET_KEY

# FIREBASE CONFIG AND INITIALIZATION
config = {
    "apiKey": FIREBASE_KEY,
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

### DB QUERY FUNCTIONS ###

# increment drink count in order history

def incrementDrinkCount(drinkName):
    currentNumOfOrder = db.child("maintainer").child(
        "orderHistory").child(drinkName).get().val()
    db.child("maintainer").child("orderHistory").child(
        drinkName).set(currentNumOfOrder + 1)

# initialize new drink to 0 if it doesnt exist in order history

def addDrink(drinkName):
    drinkHistory = db.child("maintainer").child(
        "orderHistory").child(drinkName).get().val()
    if drinkHistory == None:
        db.child("maintainer").child("orderHistory").child(drinkName).set(0)

#check if a user with a certain role is logged in using session
# parameter is role string ("maintainer" or "machine")
def isLoggedIn(role):
    checkRole = 'role' in session
    checkUsername = 'username' in session
    checkMachineId = 'machineId' in session
    if(checkRole and checkUsername and checkMachineId):
        if(session['role'] == role):
            if(session['role'] == "maintainer"):
                return True
            elif(session['role'] == "machine"):
                if(session['lock'] == True):
                    return True
                else:
                    return False
    else:
        return False

### BASIC ROUTES ###

# HOME PAGE: USER CHOOSE DRINK

@app.route("/", methods=["GET"])
def home():
    if isLoggedIn("machine"):
        db.child("status").child("orderSignal").set(False)
        drinkSetting = db.child("maintainer").child("drinkSetting").get().val()
        return render_template("home.html", drinkSetting=drinkSetting)
    elif isLoggedIn("maintainer"):
        return redirect(url_for('maintainer'))
    else:
        flash("You are not logged in as machine!", category="error")
        return redirect(url_for('login'))

# LOGIN PAGE

@app.route("/login", methods=["GET", "POST"])
def login():
    # Retrieve data from database and crosscheck with info the user has
    #  input on the login page
    # Currently login page asks for username, password, machineId

    if request.method == "POST":
        # session.pop('user', None)
        # Get login form data
        username = request.form.get("username")
        password = request.form.get("password")
        machineId = request.form.get("machineId")
        role = request.form.get("role")          

        # Get values of user's credentials from database to match the data user has
        #  entered on the Login page
        roleString = ""
        if role == "maintainer":
            roleString = "maintainerUser"
        else:
            roleString = "mainUser"
        users = db.child("users").child(roleString).get()
        lock = db.child("status").child("lock").get().val() # for machine
        if users is not None:
            for user in users.each():
                dbPassword = user.val()["password"]
                # successful login
                if(user.val()["machineId"] == machineId and user.val()["username"] == username and bcrypt.checkpw(password.encode('utf8'), dbPassword.encode('utf8'))):
                    # if role is machine check if other device already has the lock
                    session['username'] = username 
                    session['role'] = role
                    session['machineId'] = machineId  
                    if role == "machine":
                        if lock == True: 
                            if 'lock' in session: # if lock is within this device, SUCCESS
                                session.permanent = True
                                return redirect(url_for('home')) 
                            else: # if lock is on another device , fail
                                flash("Machine already set in another device!", category="error")
                                return redirect(url_for('login'))
                        else: # if lock is never set or previous owner logged out
                            db.child("status").child("lock").set(True)
                            session['lock'] = True
                            session.permanent = True
                            return redirect(url_for('home'))  #SUCCESS
                    else: # maintainer
                        session.permanent = True
                        return redirect(url_for("maintainer")) #SUCCESS
                    
        flash("Login unsuccessful", category="error")
        return redirect(url_for('login'))
    else:
        return render_template("login.html")

# REGISTER PAGE

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        realMachineId = db.child("machineId").get().val() # in real world we'll check within a list of machine id's
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        machineId = request.form.get('machineId')
        role = request.form.get("role")

        if len(username) <= 3:
            flash("username must be greater than 3 characters", category="error")
            return redirect(url_for('register'))
        elif password1 != password2:
            flash("Passwords don't match", category="error")
            return redirect(url_for('register'))
        elif len(password1) < 7:
            flash("Password must be at least 7 characters", category="error")
            return redirect(url_for('register'))
        elif machineId != realMachineId:
            flash("Invalid Machine ID!", category="error")
            return redirect(url_for('register'))
        else:
            # If user enters everything correctly, add that user to database with bcrypted password
            # to check passwords : bcrypt.checkpw(byte_password, hashed_password)
            bytepass = bytes(password2, 'utf-8')
            hashpass = bcrypt.hashpw(bytepass, bcrypt.gensalt()).decode()
            userId = str(uuid.uuid1())
            numOfMachine = len(db.child("users").child("mainUser").get().val())
            numOfMaintainer = len(db.child("users").child("maintainerUser").get().val())
            userData = {"userId":userId,"username":username,"password":hashpass,"machineId":machineId}
            if role == "maintainer" and numOfMaintainer < 5:
                maintainers = db.child("users").child("maintainerUser").get()
                if maintainers is not None:
                    for user in maintainers.each():
                        usernameDb = user.val()["username"]
                        # if username already exist
                        if(usernameDb == username):
                            flash("Username already exist!", category="error")
                            return redirect(url_for('register'))
                db.child("users").child("maintainerUser").push(userData)
            elif role == "machine" and numOfMachine < 1:
                db.child("users").child("mainUser").push(userData)
            else:
                flash("Number of accounts over limit!", category="error")
                return redirect(url_for('register'))
        return redirect(url_for('login'))
    else:
        return render_template("register.html")

@app.route("/logout", methods=["POST"])
def logout():
    checkRole = 'role' in session
    checkUsername = 'username' in session
    checkMachineId = 'machineId' in session
    if checkRole and checkUsername and checkMachineId:
        session.pop('username', None)
        session.pop('machineId', None)
        session.pop('role', None)
        if 'lock' in session:
            session.pop('lock',None)
            db.child("status").child("lock").set(False)
    flash("Logout Successfully!", category="success")
    return render_template("login.html")

# INSTRUCTION PAGE: USER PROCESS ORDER AFTER PAYMENT

@app.route("/instruction", methods=["GET"])
def instruction():
    if isLoggedIn("machine"):
        return render_template("instruction.html")
    else:
        flash("You are not logged in as machine!", category="error")
        return redirect(url_for('login'))

# MAINTAINER PAGE: MAINTAINER SETS DRINKS AND SEES PAST HISTORY

@app.route("/maintainer", methods=["GET"])
def maintainer():
    if isLoggedIn("maintainer"):
        totalProfit = db.child("maintainer").child("totalProfit").get().val()
        drinkSetting = db.child("maintainer").child("drinkSetting").get().val()
        # when machine first initialize orderHistory value is ""
        orderHistory = db.child("maintainer").child("orderHistory").get().val()
        return render_template("maintainer.html", profit=totalProfit, drinkSetting=drinkSetting, orderHistory=orderHistory)
    else:
        flash("You are not logged in as maintainer!", category="error")
        return redirect(url_for('login'))
# (TEMP) CONTROLLER: TEMPORARY PAGE FOR TESTING PUMP

@app.route("/controller", methods=["GET", "POST"])
def controller():
    statusArray = []
    for i in range(1, 7):
        status = db.child("pumps").child("pump{}".format(i)).get().val()
        if status == True:
            statusArray.append("ON")
        else:
            statusArray.append("OFF")
    return render_template("controller.html", statusArray=statusArray)

### Control Pump ###

# (TEMP) PUSH: TOGGLE PUMP ON/OFF, CONTROLLED VIA FRONTEND BUTTON

@app.route("/pump/<pumpNumber>", methods=["POST"])
def push(pumpNumber):
    pumpStatus = db.child("pumps").child(
        "pump{}".format(pumpNumber)).get().val()
    if pumpStatus == True:
        pumpStatus = False
    else:
        pumpStatus = True
    db.child("pumps").child("pump{}".format(pumpNumber)).set(pumpStatus)
    data = {"pump": pumpStatus}
    response = make_response(data)
    response.content_type = 'application/json'
    return response

### PAYMENT REST API ###

def newOrder(drinkNumber):
    drinkName = db.child("maintainer").child("drinkSetting").child(
        "drink{}".format(drinkNumber)).child("name").get().val()
    drinkPrice = db.child("maintainer").child("drinkSetting").child(
        "drink{}".format(drinkNumber)).child("price").get().val()

    # Create order request to paypal backend
    jsonData = payment.makePaypalJSON(
        "Team Kiwi Drink", "Order: {} flavor".format(drinkName), drinkPrice)
    paypalToken = payment.getToken()
    headers = {"Authorization": "Bearer {}".format(paypalToken)}
    orderData = requests.post(
        "https://api-m.sandbox.paypal.com/v2/checkout/orders", headers=headers, json=jsonData)
    jsonResponse = json.loads(orderData.content)
    orderID = jsonResponse["id"]
    paymentLink = jsonResponse["links"][1]["href"]

    # Embed Payment link in qr code
    fileName = "static/images/barcode.png"
    payment.makePaymentQR(paymentLink, fileName)

    # store order info (order id, drink type, price)
    db.child("currentOrder").child("orderID").set(orderID)
    db.child("currentOrder").child("drink").set(drinkName)
    db.child("currentOrder").child("price").set(drinkPrice)
    db.child("currentOrder").child("orderLink").set(paymentLink)
    db.child("currentOrder").child("pumpId").set(drinkNumber)

def getCurrentOrder():
    drinkName = db.child("currentOrder").child("drink").get().val()
    drinkPrice = db.child("currentOrder").child("price").get().val()
    orderID = db.child("currentOrder").child("orderID").get().val()
    return [drinkName, drinkPrice, orderID]

# PAY ORDER: open payment page, display barcode and cancel button

@app.route('/payOrder', methods=['GET'])
def payOrder():
    if isLoggedIn("machine"):
        orderInfo = getCurrentOrder()
        return render_template("payOrder.html", drink=orderInfo[0], value=orderInfo[1], orderID=orderInfo[2])
    else:
        flash("You are not logged in as machine!", category="error")
        return redirect(url_for('login'))
    

# MAKE ORDER: USE PAYPAL "MAKE ORDER" REQUEST, EMBED LINK TO BARCODE, RENDER PAY ORDER PAGE TO USER
@app.route('/makeOrder', methods=['POST'])
def makeOrder():
    if isLoggedIn("machine"):
        # Get form data
        formData = request.form  # Get form data
        if len(formData) > 0:
            drinkNumber = formData["drink"]
            newOrder(drinkNumber)
            db.child("status").child("state").set(1)
            return redirect(url_for("payOrder"))
        else:
            return redirect(url_for("home"))
    else:
        flash("You are not logged in as machine!", category="error")
        return redirect(url_for('login'))


# CANCEL ORDER: USE PAYPAL "CANCEL" ORDER REQUEST (CANCEL BUTTON IN PAYORDER.HTML)

@app.route('/cancelOrder', methods=['POST'])
def cancelOrder():
    if isLoggedIn("machine"):
        orderID = db.child("currentOrder").child("orderID").get()
        # Cancel Order
        paypalToken = payment.getToken()
        headers = {"Authorization": "Bearer {}".format(paypalToken)}
        cancelRequest = requests.delete(
            "https://api-m.sandbox.paypal.com/v1/checkout/orders/{}".format(orderID.val()), headers=headers)
        return redirect(url_for("home"))
    else:
        flash("You are not logged in as machine!", category="error")
        return redirect(url_for('login'))


# DETECT PAYMENT: USE PAYPAL "CAPTURE" ORDER REQUEST, AND USE ITS STATUS CODE TO DETECT IF AN ORDER IS COMPLETED

@app.route('/detectPayment', methods=['POST'])
def detectPayment():
    # paypal "capture" order request
    paypalToken = payment.getToken()
    orderID = db.child("currentOrder").child("orderID").get().val()
    headers = {"Authorization": "Bearer {}".format(
        paypalToken), "Content-Type": "application/json"}
    detectPayment = requests.post(
        "https://api-m.sandbox.paypal.com/v2/checkout/orders/{}/capture".format(orderID), headers=headers)

    # detect if payment is completed by its status code
    if(detectPayment.status_code == 201):
        # store order in currentorder and for maintainer's order history
        price = db.child("currentOrder").child("price").get().val()
        drinkName = db.child("currentOrder").child("drink").get().val()
        currentProfit = db.child("maintainer").child("totalProfit").get().val()
        newProfit = db.child("maintainer").child(
            "totalProfit").set(currentProfit+price)
        incrementDrinkCount(drinkName)
        # set orderSignal
        db.child("status").child("orderSignal").set(True)
        return redirect(url_for("instruction"))
    else:
        # 201 status code
        stat = Response(status=204)
        return stat

### VOICE CONTROL ###

@app.route('/detectVoice', methods=['POST'])
def detectVoice():
    voiceSignal = db.child("voiceSignal").child("isSet").get().val()
    # check if voiceSignal is set
    if voiceSignal:
        drinkNumber = db.child("voiceSignal").child("drinkNumber").get().val()
        db.child("voiceSignal").child("isSet").set(False)
        newOrder(drinkNumber)
        return redirect(url_for("payOrder"))
    else:
        stat = Response(status=204)
        return stat

### INSTRUCTION (WAIT) ###

@app.route('/waitUser', methods=['POST'])
def waitUser():
    orderSignal = db.child("status").child("orderSignal").get().val()
    irSignal = db.child("status").child("irSignal").get().val()
    state = db.child("status").child("state").get().val()
    machineStatus = {
        "orderSignal": orderSignal,
        "irSignal": irSignal,
        "state": state
    }
    machineStatusJSON = json.dumps(machineStatus)
    return machineStatusJSON

### MAINTAINER ROUTE ###

# SET DRINK: SET THE DRINK SETTING (PRICE AND NAME) IN MAINTAINER PAGE

@app.route('/setDrink', methods=['POST'])
def setDrink():
    if isLoggedIn("maintainer"):
        formData = request.form  # Get form data
        for i in range(1, 7):
            drinkName = formData["drink{}".format(i)]
            drinkPrice = 0 if float(formData["price{}".format(i)]) < 0 else float(
                formData["price{}".format(i)])
            db.child("maintainer").child("drinkSetting").child(
                "drink{}".format(i)).child("name").set(drinkName)
            db.child("maintainer").child("drinkSetting").child(
                "drink{}".format(i)).child("price").set(drinkPrice)
            addDrink(drinkName)
        return redirect(url_for("maintainer"))
    else:
        flash("You are not logged in as maintainer!", category="error")
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
