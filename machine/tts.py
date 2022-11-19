from gtts import gTTS
from playsound import playsound
import urllib3

urllib3.disable_warnings()

import os
  
mytext = 'Hello! welcome to team Kiwi Smart Dispenser machine, Please make your order by clicking the option on the screen or simply say the name of the order to the microphone .' #audio text
language = 'en' # English Language
  
myobj = gTTS(text=mytext, lang=language, slow=False)
  
# Saving converted audio
myobj.save("welcome.mp3")
  
# Playing the converted file
playsound('welcome.mp3')