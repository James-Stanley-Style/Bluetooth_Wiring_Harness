## Code developed for MAE 586 by James Stanley
## NC State Graduate School - Mechanical Engineering Department
## NCSU Project Work In Engineering
## Bluetooth Wiring Harness - Coolant Client
## Uses MLX90614 IR Thermosensor

#Import Packages
import board
import busio as io
import adafruit_mlx90614
import socket
import os
import time

def sockSetup():
    '''
        Function: sockSetup()
        Inputs: None
        Outputs: s - Connected Socket on specified Port
        Usage: Establish socket for Coolant Client code to send to and from
    '''
    serverMACAddress = 'E4:5F:01:89:A3:A2'
    port = 27
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect_ex((serverMACAddress,port))
    while s.connect_ex((serverMACAddress,port)) == 0:
        time.sleep(0.05)
    time.sleep(0.10)
    return s
try:
    #Initial the board after a brief sleep
    #Sleep included to allow Hub Pi to come up
    #Coolant Client 3rd in line of connection
    time.sleep(15.0)
    i2c = io.I2C(board.SCL, board.SDA, frequency = 20)
    #Use Adafruit Library for MLX90614
    mlx = adafruit_mlx90614.MLX90614(i2c)
    count = 0

    thermalSocket = sockSetup()
    print("Server Accepted Client")
    oldData = 0
    #Initialize Loop
    while True:

        targetTemp = "{:.3f}".format((mlx.object_temperature))
        data = float(targetTemp)
        #Check to see if old data and new data are the same
        if data != oldData:
            oldData = data

            continue
        else:
            pass

        time.sleep(0.1)
        #Use length to help pass variables in more effectively
        if len(str(data)) == 5:
            print(data)
            #Socket must send and receive to move on to the next step
            #This prevents the socket from overloading with data and reporting too slowly
            thermalSocket.send(bytes(str(data) + '//n', 'UTF-8'))
            thermalSocket.recv(8)
        if len(str(data)) == 6:
            print(data) 
            #Socket must send and recieve to move on to the next step
            #This prevents the socket from overloading with data and reporting too slowly
            thermalSocket.send(bytes(str(data) + '/n', 'UTF-8'))
            thermalSocket.recv(8)
finally:
    try:
        # Close socket to avoid hangs
        thermalSocket.close()
    except:
        pass
    #Safe shutdown for Raspberry Pi - Less chance of SD Card Corruption
    os.system("sudo shutdown now -h")

