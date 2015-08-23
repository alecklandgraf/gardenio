import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)


#Define function to measure charge time
def RC_Analog(Pin):
    counter=0
    start_time = time.time()
    #Discharge capacitor
    GPIO.setup(Pin, GPIO.OUT)
    GPIO.output(Pin, GPIO.LOW)
    time.sleep(0.1) #in seconds, suspends execution.
    GPIO.setup(Pin, GPIO.IN)
    # Count loops until voltage across capacitor reads high on GPIO
    while (GPIO.input(Pin)==GPIO.LOW):
        counter=counter+1
    end_time = time.time()
    return end_time - start_time


# Main program loop
while True:
    time.sleep(1)
    ts = time.time()
    reading = RC_Analog(25) #store counts in a variable
    counter = 0
    time_start = 0
    time_end = 0
    
    print ts, reading  #print counts using GPIO25 and time


GPIO.cleanup()
