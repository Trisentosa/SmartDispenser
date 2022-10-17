# COLLECTIONS OF PAYMENT INTEGRATION METHODS
import qrcode
import json
import requests
from requests.auth import HTTPBasicAuth

paypalToken = ""
expired = False # will be used to dynamically check for access token

# return access token
def getToken():
    global paypalToken
    global expired
    if(paypalToken == "" or expired):
        response = generateToken()
        jsonResponse = json.loads(response.content)
        paypalToken = jsonResponse["access_token"]
        print(paypalToken)

    return paypalToken

# This method will be called probably every after order. 
# If token expired during ordering, it will call this function too.
def generateToken():
    username = "AVHhJDfAZy9YwG0chra-NIq0CfhXeM9eJnWJSHL3LgN10_SCf4RsLGTcJjlDWHLeC0DdwCqc0N5nNL1w"
    password = "ELfo_kQKuB846xRcBX_7LszqVD6Gy-WJt9HnuF2DbLF53WXe1rt_mNyQqm7JM7miHwl0KmtSiqKNMfN8"
    basic = HTTPBasicAuth(username=username, password=password)
    headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type":"client_credentials"
    }
    response = requests.post("https://api-m.sandbox.paypal.com/v1/oauth2/token",auth=basic, headers=headers, data = data)
    return response

# Create QRCode and embed payment link inside
def makePaymentQR(paymentLink, fileName = "barcode.png"):
    qr = qrcode.QRCode(
        version = None, # 1 to 40, size smallest to largest. None -> use fit param to adjust automatically
        error_correction = qrcode.constants.ERROR_CORRECT_L,
        box_size = 10, # pixel of each box
        border = 4, # how many boxes thick the border should be
    )

    qr.add_data(paymentLink)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(fileName)

# Make json object order based on paypal create order API
def makePaypalJSON(productName, productDesc, productValue, currencyCode = "USD"):
    jsonData = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "items": [
                    {
                        "name": "{}".format(productName),
                        "description": "{}".format(productDesc),
                        "quantity": "1",
                        "unit_amount": {
                            "currency_code": "{}".format(currencyCode),
                            "value": "{}".format(productValue)
                        }
                    }
                ],
                "amount": {
                    "currency_code": "{}".format(currencyCode),
                    "value": "{}".format(productValue),
                    "breakdown": {
                        "item_total": {
                            "currency_code": "{}".format(currencyCode),
                            "value": "{}".format(productValue)
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
    return jsonData