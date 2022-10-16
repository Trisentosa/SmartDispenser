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

### BASIC ROUTES ###
@app.route("/", methods=["GET"])
def home():
    drinkSetting = db.child("maintainer").child("drinkSetting").get().val()
    return render_template("home.html", drinkSetting=drinkSetting)

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/maintainer", methods=["GET"])
def maintainer():
    totalProfit = db.child("maintainer").child("totalProfit").get().val()
    drinkSetting = db.child("maintainer").child("drinkSetting").get().val()
    return render_template("maintainer.html", profit=totalProfit, drinkSetting=drinkSetting)

@app.route("/controller", methods=["GET","POST"])
def controller():
    statusArray = []
    for i in range(1,7):
        status = db.child("pumps").child("pump{}".format(i)).get().val()
        if status == True:
            statusArray.append("ON")
        else:
            statusArray.append("OFF")

    if request.method == 'GET':
        #Get request is temporary only
        return render_template("controller.html", statusArray=statusArray)
    else:
        paypalToken = payment.getToken() 
        orderID = db.child("currentOrder").child("orderID").get().val()
        headers = {"Authorization":"Bearer {}".format(paypalToken), "Content-Type": "application/json"}
        detectPayment = requests.post("https://api-m.sandbox.paypal.com/v2/checkout/orders/{}/capture".format(orderID), headers=headers)
        if(detectPayment.status_code == 422):
            stat = Response(status=204)
            return stat 
        else:
            #201 status code
            price = db.child("currentOrder").child("price").get().val()
            currentProfit = db.child("maintainer").child("totalProfit").get().val()
            newProfit = db.child("maintainer").child("totalProfit").set(currentProfit+price)
            return render_template("controller.html", statusArray=statusArray)

### Control Pump ###

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

@app.route('/makeOrder', methods=['POST'])
def makeOrder():
    # Get form data
    formData = request.form # Get form data
    drinkNumber = formData["drink"]
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

    return render_template("payOrder.html", drink=drinkName, value = drinkPrice, orderID=orderID, paypalToken=paypalToken)

@app.route('/cancelOrder', methods=['POST'])
def cancelOrder():
    orderID = db.child("currentOrder").child("orderID").get()

    #Cancel Order
    paypalToken = payment.getToken() 
    headers = {"Authorization":"Bearer {}".format(paypalToken)}
    cancelRequest = requests.delete("https://api-m.sandbox.paypal.com/v1/checkout/orders/{}".format(orderID.val()), headers=headers)
    print(cancelRequest.status_code)
    return redirect(url_for("home") )

### MAINTAINER ROUTE ### 
@app.route('/setDrink', methods=['POST'])
def setDrink():
    formData = request.form # Get form data
    print(formData)
    for i in range(1,7):
        drinkName = formData["drink{}".format(i)]
        drinkPrice = 0 if float(formData["price{}".format(i)]) < 0 else float(formData["price{}".format(i)])
        db.child("maintainer").child("drinkSetting").child("drink{}".format(i)).child("name").set(drinkName)
        db.child("maintainer").child("drinkSetting").child("drink{}".format(i)).child("price").set(drinkPrice)
    return redirect(url_for("home") )

if __name__ == '__main__':
    app.run(debug=True)


