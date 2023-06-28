import RPi.GPIO as GPIO
import time, sys
import sqlite3
import queue

HALL_EFFECT_GPIO = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(HALL_EFFECT_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Connect to the database
conn = sqlite3.connect('/home/pi/Documents/Baja 2023/Fuel Data 2')
c = conn.cursor
cursor = conn.cursor()

rotationsTotal = 0
rotationsTemp = 0
q = queue.Queue()

for i in range (480):
    q.put(0)

def hallPulse(channel):
    global rotationsTemp
    rotationsTemp += 1

# Causes the hallPulse() function to run when a pulse is sent into pin 26
GPIO.add_event_detect(HALL_EFFECT_GPIO, GPIO.FALLING, callback=hallPulse)

while True:
    try:
        q.put(rotationsTemp)
        rotationsDumped = q.get()
        
        rotationsTotal = rotationsTotal + rotationsTemp - rotationsDumped
        
        rotationsTemp = 0
        
        rps = 0.42 * rotationsTotal
        mph = 0.414 * rps # Constant Derivation in System Specification Document
        #mph = round(mph, 5)
        
        conn.execute("DELETE FROM speed")
        conn.execute("INSERT INTO speed VALUES (?)", (mph, ))
        conn.commit()
        
        time.sleep(0.005)
    
    except KeyboardInterrupt:
        print('\nkeyboard interrupt!')
        # This makes sure that the input from the gpio ports stops
        GPIO.cleanup()
        conn.close()
        sys.exit()
