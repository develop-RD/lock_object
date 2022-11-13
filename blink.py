import wiringpi
import time
import sys
from wiringpi import GPIO

NUM = 17    #26pin
pinLed = 3
wiringpi.wiringPiSetup()

for i in range(0, NUM):
    wiringpi.pinMode(i, GPIO.OUTPUT) ;

while True:
    wiringpi.digitalWrite(pinLed, GPIO.HIGH)
    time.sleep(1)
    wiringpi.digitalWrite(pinLed, GPIO.LOW)
    time.sleep(1)
