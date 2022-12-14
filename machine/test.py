# #!/usr/bin/python3
# import RPi.GPIO as GPIO
# import time
 
# in1 = 17
# in2 = 18
# in3 = 27
# in4 = 22
 
# # lower -> faster turn speed. lowest is around 0.002
# step_sleep = 0.003
 
# step_count = 4096 # 5.625*(1/64) per step, 4096 steps is 360°, 4096 = 1 rotation
 
# # defining stepper motor sequence
# step_sequence = [[1,0,0,1],
#                  [1,0,0,0],
#                  [1,1,0,0],
#                  [0,1,0,0],
#                  [0,1,1,0],
#                  [0,0,1,0],
#                  [0,0,1,1],
#                  [0,0,0,1]]
 
# # motor setting up
# GPIO.setmode( GPIO.BCM )
# GPIO.setup( in1, GPIO.OUT )
# GPIO.setup( in2, GPIO.OUT )
# GPIO.setup( in3, GPIO.OUT )
# GPIO.setup( in4, GPIO.OUT )
 
# # initializing
# GPIO.output( in1, GPIO.LOW )
# GPIO.output( in2, GPIO.LOW )
# GPIO.output( in3, GPIO.LOW )
# GPIO.output( in4, GPIO.LOW )
 
 
# motor_pins = [in1,in2,in3,in4]
# motor_step_counter = 0 ;
 
 
# def cleanup():
#     GPIO.output( in1, GPIO.LOW )
#     GPIO.output( in2, GPIO.LOW )
#     GPIO.output( in3, GPIO.LOW )
#     GPIO.output( in4, GPIO.LOW )
#     GPIO.cleanup()
 
 
# # the meat
# try:
#     print("start rotating")
#     i = 0
#     for i in range(step_count):
#         for pin in range(0, len(motor_pins)):
#             GPIO.output( motor_pins[pin], step_sequence[motor_step_counter][pin] )
#         motor_step_counter = (motor_step_counter - 1) % 8 # clockwise, cc +1 instead
#         time.sleep( step_sleep )
#     print("finish rotating")
 
# except KeyboardInterrupt:
#     cleanup()
#     exit( 1 )
 
# cleanup()
# exit( 0 )

import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00005)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            if dist < 7:
               print("cup present")
            print ("Measured Distance = %.1f cm" % dist)
            time.sleep(0.5)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
