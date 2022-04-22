## Code developed for MAE 586 by James Stanley
## NC State Graduate School - Mechanical Engineering Department
## NCSU Project Work In Engineering
## Bluetooth Wiring Harness - Gear Client
## Uses ADXL343 Accelerometer
import time
import board
import adafruit_adxl34x
import socket
import os

def sockSetup():
    '''
        Function: sockSetup()
        Inputs: None
        Outputs: s - Connected Socket on specified Port
        Usage: Establish socket for gear Client code to send to and from
    '''
    serverMACAddress = 'E4:5F:01:89:A3:A2'
    port = 28
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect_ex((serverMACAddress,port))
    while s.connect_ex((serverMACAddress,port)) == 0:
        time.sleep(0.25)
    return s
#Initialize I2C Comms
i2c = board.I2C()


#Use Adafruit's accelerometer Library
accelerometer = adafruit_adxl34x.ADXL343(i2c)
# Initial the board after a brief sleep
#Sleep included to allow Hub Pi to come up
time.sleep(2.0)
print("Trying to connect...")
#Initialize Socket
gearSocket = sockSetup()


try:
    #Initialize Loop
    while True:
        (x,y,z) = accelerometer.acceleration
        x = round(x,2)
        y = round(y,2)
        z = round(z,2)

        if (x < -2.0) and (y > 2.0) and (z > 2.0):
            Gear = '1.0000'
        elif (x > 2.0) and (y > 2.0) and (z > 2.0):
            Gear = '2.0000'
        elif (x < -2.0) and (y > 2.0) and (-2.0 < z < 2.0):
            Gear = '3.0000'
        elif (x > 2.0) and  (y > 2.0) and (-2.0 < z < 2.0):
            Gear = '4.0000'
        elif (x < -2.0) and (y > 2.0) and (z < -2.0):
            Gear = '5.0000'
        elif (x > 2.0) and (y > 2.0) and (z < -2.0):
            Gear = '6.0000'
        else:
            Gear = '0.0000'

        print("Current Gear: " + Gear)
        time.sleep(0.05)
        # Socket must send and receive to move on to the next step
        # This prevents the socket from overloading with data and reporting too slowly
        gearSocket.send(bytes(str(Gear) + '/n' , 'UTF-8'))
        gearSocket.recv(8)
finally:
    #Close socket to avoid hangs
    gearSocket.close()
    # Safe shutdown for Raspberry Pi - Less chance of SD Card Corruption
    os.system("sudo shutdown now -h")

