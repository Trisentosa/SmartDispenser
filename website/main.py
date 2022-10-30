from flask import Flask, render_template, request, redirect, url_for, make_response, Response
import requests
import os
from requests.auth import HTTPBasicAuth
import pyrebase
import json
import payment

app = Flask(__name__)
app.config['SECRET_KEY'] = "tempkey" #encrypts cookies and session data related to website

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

### DB QUERY FUNCTIONS ###

# increment drink count in order history
def incrementDrinkCount(drinkName):
    currentNumOfOrder = db.child("maintainer").child("orderHistory").child(drinkName).get().val()
    db.child("maintainer").child("orderHistory").child(drinkName).set(currentNumOfOrder + 1)

# initialize new drink to 0 if it doesnt exist in order history
def addDrink(drinkName):
    drinkHistory = db.child("maintainer").child("orderHistory").child(drinkName).get().val()
    if drinkHistory == None:
        db.child("maintainer").child("orderHistory").child(drinkName).set(0)

### BASIC ROUTES ###

# HOME PAGE: USER CHOOSE DRINK
@app.route("/", methods=["GET"])
def home():
    db.child("status").child("orderSignal").set(False)
    drinkSetting = db.child("maintainer").child("drinkSetting").get().val()
    return render_template("home.html", drinkSetting=drinkSetting)

# LOGIN PAGE
@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

# REGISTER PAGE
@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

# INSTRUCTION PAGE: USER PROCESS ORDER AFTER PAYMENT
@app.route("/instruction", methods=["GET"])
def instruction():
    return render_template("instruction.html")

# MAINTAINER PAGE: MAINTAINER SETS DRINKS AND SEES PAST HISTORY
@app.route("/maintainer", methods=["GET"])
def maintainer():
    totalProfit = db.child("maintainer").child("totalProfit").get().val()
    drinkSetting = db.child("maintainer").child("drinkSetting").get().val()
    # when machine first initialize orderHistory value is ""
    orderHistory = db.child("maintainer").child("orderHistory").get().val()
    return render_template("maintainer.html", profit=totalProfit, drinkSetting=drinkSetting, orderHistory = orderHistory)

# (TEMP) CONTROLLER: TEMPORARY PAGE FOR TESTING PUMP
@app.route("/controller", methods=["GET","POST"])
def controller():
    statusArray = []
    for i in range(1,7):
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
    pumpStatus = db.child("pumps").child("pump{}".format(pumpNumber)).get().val()
    if pumpStatus == True:
        pumpStatus = False
    else:
        pumpStatus = True
    db.child("pumps").child("pump{}".format(pumpNumber)).set(pumpStatus)
    data = {"pump":pumpStatus}
    response = make_response(data)
    response.content_type = 'application/json'
    return response

### PAYMENT REST API ###  

def newOrder(drinkNumber):
    drinkName = db.child("maintainer").child("drinkSetting").child("drink{}".format(drinkNumber)).child("name").get().val()
    drinkPrice = db.child("maintainer").child("drinkSetting").child("drink{}".format(drinkNumber)).child("price").get().val()

    # Create order request to paypal backend
    jsonData = payment.makePaypalJSON("Team Kiwi Drink", "Order: {} flavor".format(drinkName), drinkPrice)
    paypalToken = payment.getToken() 
    headers = {"Authorization":"Bearer {}".format(paypalToken)}
    orderData = requests.post("https://api-m.sandbox.paypal.com/v2/checkout/orders", headers=headers, json=jsonData)
    jsonResponse = json.loads(orderData.content)
    orderID = jsonResponse["id"]
    paymentLink = jsonResponse["links"][1]["href"]

    #Embed Payment link in qr code
    fileName = "static/images/barcode.png"
    payment.makePaymentQR(paymentLink, fileName) 

    #store order info (order id, drink type, price)
    db.child("currentOrder").child("orderID").set(orderID)
    db.child("currentOrder").child("drink").set(drinkName)
    db.child("currentOrder").child("price").set(drinkPrice)
    db.child("currentOrder").child("orderLink").set(paymentLink)
    db.child("currentOrder").child("pumpId").set(drinkNumber)

def getCurrentOrder():
    drinkName = db.child("currentOrder").child("drink").get().val()
    drinkPrice = db.child("currentOrder").child("price").get().val()
    orderID = db.child("currentOrder").child("orderID").get().val()
    return [drinkName,drinkPrice,orderID]

# PAY ORDER: open payment page, display barcode and cancel button
@app.route('/payOrder',methods=['GET'])
def payOrder():
    orderInfo = getCurrentOrder()
    return render_template("payOrder.html", drink=orderInfo[0], value = orderInfo[1], orderID=orderInfo[2])


# MAKE ORDER: USE PAYPAL "MAKE ORDER" REQUEST, EMBED LINK TO BARCODE, RENDER PAY ORDER PAGE TO USER
@app.route('/makeOrder', methods=['POST'])
def makeOrder():
    # Get form data
    formData = request.form # Get form data
    if len(formData) > 0:
        drinkNumber = formData["drink"]
        newOrder(drinkNumber)
        db.child("status").child("state").set(1)
        return redirect(url_for("payOrder"))
    else:
        return redirect(url_for("home"))    

# CANCEL ORDER: USE PAYPAL "CANCEL" ORDER REQUEST (CANCEL BUTTON IN PAYORDER.HTML)
@app.route('/cancelOrder', methods=['POST'])
def cancelOrder():
    orderID = db.child("currentOrder").child("orderID").get()

    #Cancel Order
    paypalToken = payment.getToken() 
    headers = {"Authorization":"Bearer {}".format(paypalToken)}
    cancelRequest = requests.delete("https://api-m.sandbox.paypal.com/v1/checkout/orders/{}".format(orderID.val()), headers=headers)
    return redirect(url_for("home") )

# DETECT PAYMENT: USE PAYPAL "CAPTURE" ORDER REQUEST, AND USE ITS STATUS CODE TO DETECT IF AN ORDER IS COMPLETED
@app.route('/detectPayment', methods=['POST'])
def detectPayment():
    # paypal "capture" order request
    paypalToken = payment.getToken() 
    orderID = db.child("currentOrder").child("orderID").get().val()
    headers = {"Authorization":"Bearer {}".format(paypalToken), "Content-Type": "application/json"}
    detectPayment = requests.post("https://api-m.sandbox.paypal.com/v2/checkout/orders/{}/capture".format(orderID), headers=headers)
    
    # detect if payment is completed by its status code
    if(detectPayment.status_code == 201):
        #store order in currentorder and for maintainer's order history
        price = db.child("currentOrder").child("price").get().val()
        drinkName = db.child("currentOrder").child("drink").get().val()
        currentProfit = db.child("maintainer").child("totalProfit").get().val()
        newProfit = db.child("maintainer").child("totalProfit").set(currentProfit+price)
        incrementDrinkCount(drinkName)
        #set orderSignal
        db.child("status").child("orderSignal").set(True)
        return redirect(url_for("instruction") )
    else:
        #201 status code
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

### MAINTAINER ROUTE ### 

# SET DRINK: SET THE DRINK SETTING (PRICE AND NAME) IN MAINTAINER PAGE
@app.route('/setDrink', methods=['POST'])
def setDrink():
    formData = request.form # Get form data
    for i in range(1,7):
        drinkName = formData["drink{}".format(i)]
        drinkPrice = 0 if float(formData["price{}".format(i)]) < 0 else float(formData["price{}".format(i)])
        db.child("maintainer").child("drinkSetting").child("drink{}".format(i)).child("name").set(drinkName)
        db.child("maintainer").child("drinkSetting").child("drink{}".format(i)).child("price").set(drinkPrice)
        addDrink(drinkName)
    return redirect(url_for("home") )


if __name__ == '__main__':
    app.run(debug=True)