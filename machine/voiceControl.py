import speech_recognition as sr
import pyttsx3
#machine state:
# 0: wait for someone to speak
# 1: wait for order signal

recognizer = sr.Recognizer()
state = 0
words = ["1","2","3","4","5","6","milk","coffee","green tea"]

while True:
    if state == 0:
        try:
            with sr.Microphone() as mic:
                print("listening")
                recognizer.adjust_for_ambient_noise(mic, duration=0.1)
                audio = recognizer.listen(mic)

                text = recognizer.recognize_google(audio)
                text = text.lower()
                
                print(text)
                if(text in words):
                    state = 1
        except sr.UnknownValueError:
            print("unknown val")
            recognizer = sr.Recognizer()
            continue
    else:
        print("In state 1, waiting for order signal")
    



