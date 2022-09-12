from flask import Flask, render_template, request, redirect, url_for, make_response
import requests
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

# Routes
@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/maintainer", methods=["GET"])
def maintainer():
    return render_template("maintainer.html")

### PAYMENT REST API ###

@app.route('/makeOrder', methods=['POST'])
def makeOrder():
    jsonData = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "items": [
                    {
                        "name": "T-Shirt",
                        "description": "Green XL",
                        "quantity": "1",
                        "unit_amount": {
                            "currency_code": "USD",
                            "value": "20"
                        }
                    }
                ],
                "amount": {
                    "currency_code": "USD",
                    "value": "20",
                    "breakdown": {
                        "item_total": {
                            "currency_code": "USD",
                            "value": "20"
                        }
                    }
                }
            }
        ],
        "application_context": {
            "return_url": "https://example.com/return",
            "cancel_url": "https://example.com/cancel"
        }
    }
    headers = {"Authorization":"Bearer {}".format(payment.getToken())}
    orderData = requests.post("https://api-m.sandbox.paypal.com/v2/checkout/orders", headers=headers, json=jsonData)
    jsonResponse = json.loads(orderData.content)
    paymentLink = jsonResponse["links"][1]["href"]
    fileName = "barcode.png"
    payment.makePaymentQR(paymentLink, fileName)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

