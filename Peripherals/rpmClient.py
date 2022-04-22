## Code developed for MAE 586 by James Stanley
## NC State Graduate School - Mechanical Engineering Department
## NCSU Project Work In Engineering
## Bluetooth Wiring Harness - Gear Client
## Uses ADXL343 Accelerometer
import RPi.GPIO as GPIO
from time import sleep
import pigpio
from read_RPM import reader
import os
import time
import socket
#from gpiozero import CPUTemperature

# NECESSARY!! System MUST initialize pigpio Daemon prior to running this code!
# In this case, this is handled outside of the Python Code, but a commented out version is included
# For ease of use
#os.system('sudo pigpiod')

# Initial the board after a brief sleep
# Sleep included to allow Hub Pi to come up
time.sleep(12)

def sockSetup():
    '''
        Function: sockSetup()
        Inputs: None
        Outputs: s - Connected Socket on specified Port
        Usage: Establish socket for RPM Client code to send to and from
    '''
    serverMACAddress = 'E4:5F:01:89:A3:A2'
    port = 26
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect_ex((serverMACAddress,port))
    while s.connect_ex((serverMACAddress,port)) == 0:
        time.sleep(0.5)

    return s

def twentyFiveRound(x, base=25):
    '''
        Function: twentyFiveRound
        Inputs: X - Float or Int
                base - Int, defaults to 25
        Outputs: Rounded value
        Usage: Round the RPM output to the nearest 25 for ease of reading and handling
    '''
    return base * round(x/base)

A = time.time()

#Use PiGPIO library's Tachometer Feature
RPMList = []
pi = pigpio.pi()
RPM_GPIO = 16
Sample_Time = 2.0
tach = reader(pi,RPM_GPIO)
time.sleep(1.0)
rpmSocket = sockSetup()
count = 0
try:
    #Initialize Loop
    while True:
        try:
            #Read RPM
            rpm = tach.RPM()
            RPMList.append(twentyFiveRound(rpm))
            count += 1
            if count == 10:
                #Since this reads pretty quick, take the average of the last 10 runs
                AvgRPM = (sum(RPMList)/len(RPMList))
                print(AvgRPM)
                if AvgRPM > 6400:
                    '''NOTE: This part lead to some jumpiness in the code, but prevent the Hub from breaking
                    In future iterations of this code, it might be best to just ignore values over 7000 from an average
                    Perspective, rather than passing 0 to the hub. 
                    '''
                    # Socket must send and receive to move on to the next step
                    # This prevents the socket from overloading with data and reporting too slowly
                    rpmSocket.send(bytes(str(0.0) + '/n','UTF-8'))
                    rpmSocket.recv(8)
                    count = 0
                    RPMList = []
                else:
                    count = 0
                    RPMList = []
                    # Socket must send and receive to move on to the next step
                    # This prevents the socket from overloading with data and reporting too slowly
                    rpmSocket.send(bytes(str(AvgRPM) + '/n', 'UTF-8'))
                    rpmSocket.recv(8)


        except RuntimeError:
            pass

finally:
    #Remove Pi Daemon
    pi.stop()
    #Safely close socket
    rpmSocket.close()
    # Safe shutdown for Raspberry Pi - Less chance of SD Card Corruption
    os.system('sudo shutdown now -h')

