from gtts import gTTS
from playsound import playsound
import urllib3
import os

urllib3.disable_warnings()
language = 'en' # English Language

#welcomeText = 'Hello! welcome to team Kiwi Smart Dispenser, order by tapping the option on the screen or saying the name of the drink to the microphone' #audio text
orderCompleteText = "Order successful! To continue, scan the barcode and pay via paypal"
#paymentCompleteText = "Payment complete. To continue, please place cup on the tray"
#makingOrderText = "Making the order ... "
#orderDoneText = "Thank you! have a good rest of your day"


#welcomeObj = gTTS(text=welcomeText, lang=language, slow=False)
orderCompleteObj = gTTS(text=orderCompleteText, lang=language, slow=False)
#paymentCompleteObj = gTTS(text=paymentCompleteText, lang=language, slow=False)
#makingOrderObj = gTTS(text=makingOrderText, lang=language, slow=False)
#orderDoneObj = gTTS(text=orderDoneText, lang=language, slow=False)
  
# # Saving converted audio
# welcomeObj.save("audio/welcome.mp3")
orderCompleteObj.save("audio/orderComplete.mp3")
#paymentCompleteObj.save("audio/paymentComplete.mp3")
#makingOrderObj.save("audio/makingOrder.mp3")
# orderDoneObj.save("audio/orderDone.mp3")
  
# Playing the converted file
#playsound('audio/welcome.mp3')
playsound('audio/orderComplete.mp3')
#playsound('audio/paymentComplete.mp3')
#playsound('audio/makingOrder.mp3')
#playsound('audio/orderDone.mp3')
