## Code developed for MAE 586 by James Stanley
## NC State Graduate School - Mechanical Engineering Department
## NCSU Project Work In Engineering
## Bluetooth Wiring Harness - Speedo Client
## Uses Ultimate GPS by Adafruit

import time
import board
import serial
import busio
import socket
import os

import adafruit_gps

def sockSetup():
    '''
        Function: sockSetup()
        Inputs: None
        Outputs: s - Connected Socket on specified Port
        Usage: Establish socket for Speedo Client code to send to and from
    '''
    serverMACAddress = 'E4:5F:01:89:A3:A2'
    port = 25
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect_ex((serverMACAddress,port))
    while s.connect_ex((serverMACAddress,port)) == 0:
        time.sleep(0.25)
    #s.connect((serverMACAddress,port))
    time.sleep(.01)
    return s

# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
#uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)

# for a computer, use the pyserial library for uart access
# import serial

#Initial the board after a brief sleep
#Sleep included to allow Hub Pi to come up
time.sleep(10)
#UART Comms initialized
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)

#GPS Comms initialized, GPS Starts to find a fix
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial
#NMEA Standards, only request Speed Data
gps.send_command(b'PMTK314,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
#Update GPS at 10 Hz (10 updates per second)
gps.send_command(b'PMTK220,100')

i = 1
firstRun = True
gpsSocket = sockSetup()
print("Server Accepted Client")
A = time.time()
try:
    #Initialize Main Loop
    while True:
        A = time.time()
        gps.update()
        if firstRun:
            #Clear out First Read Buffer
            data = gps.read(81)
            firstRun = False
            data_line = gps.readline()

        data_line = gps.readline()
        #If not Speed Data, Pass, Else, use
        if data_line is not None and 'NVTG' in str(data_line):
            #data_string = "".join([chr(b) for b in data])
            #Find point in the data string for M/S
            data_string = str(data_line).split(",")
            #speedKn = data_string[5]
            speedMs = data_string[7]
            #Convert to MPH
            data = str(round(float(speedMs) * 2.237,3))
            print(data)
            #print("Speed in mph: " + str(float(speedMs) * 2.237))
            if str(data) == '0.0':
                #pass
                print(data)
                # Socket must send and receive to move on to the next step
                # This prevents the socket from overloading with data and reporting too slowly
                gpsSocket.send(bytes(str(data) + '////n','UTF-8'))
                gpsSocket.recv(8)
            if len(str(data)) == 5:
                print(data)
                # Socket must send and receive to move on to the next step
                # This prevents the socket from overloading with data and reporting too slowly
                gpsSocket.send(bytes(str(data) + '//n', 'UTF-8'))
                gpsSocket.recv(8)
            if len(str(data)) == 6:
                print(data)
                # Socket must send and receive to move on to the next step
                # This prevents the socket from overloading with data and reporting too slowly
                gpsSocket.send(bytes(str(data) + '/n', 'UTF-8'))
                gpsSocket.recv(8)


            
        

finally:
    #Close Socket safely
    gpsSocket.close()
    print("Socket Closed")
    # Safe shutdown for Raspberry Pi - Less chance of SD Card Corruption
    os.system("sudo shutdown now -h")
