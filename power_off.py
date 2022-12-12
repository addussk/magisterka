# Power off script
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(36, GPIO.IN)

while(True):
	print(GPIO.input(36))
	time.sleep(0.2)
