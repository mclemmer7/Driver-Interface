import RPi.GPIO as GPIO
import time, sys
import sqlite3


FLOW_SENSOR_GPIO = 13
BUTTON_SENSOR_GPIO = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# For button
GPIO.setup(BUTTON_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)


conn = sqlite3.connect('/home/pi/Documents/Baja 2023/Fuel Data 2')
c = conn.cursor
cursor = conn.cursor()
#var = 10
#conn.execute("DELETE FROM fuelFlow(numCount) WHERE ID 1")
#conn.execute("INSERT INTO fuelFlow(numCount) VALUES (" + str(var) + ")")
#conn.commit()
#conn.close()


# If the database has any values in it, pull the most recent value for fuelID and totalCount
# Else, initialize totalCount, count, and fuelID to 0

global count # Number of rotations of the fuel flow sensor for a given 1 second interval
count = 0
global totalCount # Total number of rotations since the code was first ran
totalCount = 0
global fuelID
fuelID = 0
global percent

print("Initial fuelID:" + str(fuelID))

def countPulse(channel):
   global count
   global totalCount
   totalCount += 1
   if start_counter == 1:
      count += count

# Causes the countPulse() function to run when a pulse is sent into pin 13
GPIO.add_event_detect(FLOW_SENSOR_GPIO, GPIO.FALLING, callback=countPulse)

# We are grabbing the id array and rotations array from the database to convert it
# to an integer
idArray = conn.execute("SELECT id FROM fuelFlow")
rotationsArray = conn.execute("SELECT rotations FROM fuelFlow")
conn.commit()
newCount = 0;

# Go through the array and we only want the value at index 1 since it is the most recent piece
# of data in the database
for i in rotationsArray:
    if newCount == 1:
        countString = i
        # Turn it into a string, then get the substring, which can be converted to an integer
        holdCount = str(countString)
        stop = holdCount.find(",")
        hold = int(holdCount[1:stop])
        break;
        
    newCount += 1
    
totalCount = hold
print(totalCount)

# Reset the count to 0
newCount = 0
# Go through idArray to get the current fuel ID
for i in idArray:
    if newCount == 1:
        countString = i
        holdCount = str(countString)
        stop = holdCount.find(",")
        hold = int(holdCount[1:stop])
    newCount += 1

fuelID = hold
print (fuelID)

while True:
    try:
        start_counter = 1
        time.sleep(1)
        start_counter = 0
        
        # Check for button press. GPIO pin is pulled to ground on button press
        if GPIO.input(BUTTON_SENSOR_GPIO) == 0:
            # Reset the global variables
            totalCount = 0
            fuelID = 0
            # Remove all the fuel data from the database
            conn.execute("DELETE FROM fuelFlow")
            conn.commit()
            print("BUTTON IS PRESSED!")
#             time.sleep(10)
        
        # 5880 is the amount of pulses for one liter
        # flow = (totalCount / 5880) # Pulse frequency (Hz) = 7.5Q, Q is flow rate in L/min.

        # Tank holds 1.5 Gallons, which is about 5.678 Liters, or about 30000 pulses/rotations of
        # the fuel flow sensor
        remainingCnt = 30000 - totalCount
        print("Remaining Count in pulses: " + str(remainingCnt))
        # Round the percent to 5 decimal places
        percent = round((1- (totalCount/30000)), 5)
        
        print("Percentage of remaining fuel: " + str(percent))
        print("Total Count: " + str(totalCount)) # Total Number of FFS rotations during the code start
        
        # Increment the fuelId, which is the count for the database
        fuelID = fuelID + 1
        print("fuelID: " +str(fuelID))
        # Add the most recent values for fuelID, totalCount, and percent into the database
        conn.execute("INSERT OR IGNORE INTO fuelFlow VALUES (?,?,?)", (fuelID, totalCount, percent))
        
        # Delete the old piece of data from the first row of the table
        conn.execute("DELETE FROM fuelFlow WHERE id=" + str(fuelID - 2))
        conn.commit()
        
        # It takes the loop about 1 second for each iteration
        time.sleep(1)
        
    except KeyboardInterrupt:
        print('\nkeyboard interrupt!')
        # This makes sure that the input from the gpio ports stops
        GPIO.cleanup()
        conn.close()
        sys.exit()
        

