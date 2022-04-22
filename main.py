## Code developed for MAE 586 by James Stanley
## NC State Graduate School - Mechanical Engineering Department
## NCSU Project Work In Engineering
## Bluetooth Wiring Harness - Hub System
## Requires no additional hardware

import pygame
import random
import socket
import time
import select
import threading
from threading import Timer
from subprocess import call

def setupSocketThreads(MACAddress, numSockets):
	'''
	 	Function: setuptSocketThreads()
        	Inputs: MACAddress - String containing Hub Mac Address
			numSockets - Int representing the desired number of sockets to create
				     - Max for Raspberry Pi 4B is 8 bluetooth connections (assuming none outstanding)
        	Outputs: server - Dictionary of numSockets length used to handle the socket swapping. 
				  Dictionary contains Connection information - Socket Number, Client, Address
        	Usage: Set up sockets at the start of the code to initialize the connection. 
			This prevents dropout due to connections not existing
	'''
	
    if numSockets > 4:
        print("Too Many Sockets!")
        quitCondition = True
    ports = {}
    sockets = {}
    server = {}
    backlog = numSockets
    socketImage = []
    # Prep socket Connection image, one for each socket
    socketImage.append(pygame.image.load('/home/pi/bluetoothHarness/bluetooth-harness-main/Gauges/Connections/speedometer.png'))
    socketImage.append(pygame.image.load('/home/pi/bluetoothHarness/bluetooth-harness-main/Gauges/Connections/tachometer.png'))
    socketImage.append(pygame.image.load('/home/pi/bluetoothHarness/bluetooth-harness-main/Gauges/Connections/coolant.png'))
    socketImage.append(pygame.image.load('/home/pi/bluetoothHarness/bluetooth-harness-main/Gauges/Connections/gear.png'))
    size = 32
    for i in range(0, numSockets):
	#Loop operates on Ports 25+ to avoid any restricted ports 
        ports[i] = 25 + i
        sockets[i] = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        # sockets[i].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sockets[i].setblocking(0)
        sockets[i].bind((MACAddress, ports[i]))
        sockets[i].listen(backlog)
    for i in range(0,numSockets):

        client, address = sockets[i].accept()
        print("Socket " + str(i) + "  Accepted")
	# Each time a connection is made, the representative connection image should flash on screen
	# This ensures the user is able to understand how things are initializing
        gameDisplay.blit(socketImage[i], (50, 100 + i*100))
        server[i] = [sockets[i], client, address]
        pygame.display.update()
        initialized = True

    return server


def socketThread(server, socketNum, StartTime):
	'''
	 Function: socketThread()
        Inputs: server - Server Dictionary for specificed socket, containing necessary socket information
	 	socketNum - Int, Socket count (Max = numSocket)
		StartTime - Time type object
        Outputs: None
        Usage: Uses globals to update the current data for each gauge.
		Handles all gauges seperately so it can be run as a thread
	'''
    # print("Socket " ,socketNum, "is running")
    global gpsData
    global tempData
    global gearData
    global rpmData
    socket = server[0]
    client = server[1]
    address = server[2]
    size = 8
    if socketNum == 0:
        ready = select.select([client], [], [], 0.1)
        try:
            if ready[0]:
                data = client.recv(size)
                if data != 0:
                    gpsData = str(data)
                    client.send(bytes(str("Received"),'UTF-8'))
                    return gpsData
                else:
                    #input("Pause Here - Socket 0")
                    pass
        except:
            pass
    if socketNum == 1:
        ready = select.select([client], [], [], 0.1)
        try:
            # print("Socket " ,socketNum, "is listening")
            if ready[0]:
                data = client.recv(size)
                if data != 0:
                    rpmData= str(data)
                    client.send(bytes(str("Received"),'UTF-8'))
                    return 0
                else:
                    #input("Pause Here - Socket 1")
                    pass

        except:
            pass
    if socketNum == 2:
        ready = select.select([client], [], [], 0.1)
        try:
            # print("Socket " ,socketNum, "is listening")
            if ready[0]:
                data = client.recv(size)
                if data != 0:
                    tempData = str(data)
                    client.send(bytes(str("Received"),'UTF-8'))
                    return 0
                else:
                    #input("Pause Here")
                    pass
        except:
            pass
    if socketNum == 3:
        ready = select.select([client], [], [], 0.1)
        try:
            # print("Socket " ,socketNum, "is listening")
            if ready[0]:
                data = client.recv(size)
                if data != 0:
                    gearData = str(data)
                    client.send(bytes(str("Received"),'UTF-8'))
                    return 0
                else:
                    #input("Pause Here")
                    pass
        except:
            pass


def socketParse(data):
	'''
	 Function: socketParse()
        Inputs: data - String or Bytes Type
        Outputs: parsedData - Float type data representing the usable result from the sockets
        Usage: Used to remove the trailing slashes and new line indicators from a socket packet
		These were included to ensure all sockets pass 8 bytes of data, and must be removed
		prior to utilization
	'''
    if data is not None and type(data) is not int:
        if "////n" in data:
            parsedData = float(data.replace("b'", '').replace("////n'", ''))
            return parsedData
        elif "///n" in data:
            parsedData = float(data.replace("b'", '').replace("///n'", ''))
            return parsedData
        elif "//n" in data:
            parsedData = float(data.replace("b'",'').replace("//n'",''))
            return parsedData
        else:
            parsedData = float(data.replace("b'", '').replace("/n'", ''))
            return parsedData
    else:
        return 0.0

def gaugeRPM(x, y):
	'''
	 Function: gaugeRPM()
        Inputs: x,y - Int type values representing gauge location
        Outputs: None
        Usage: Updates specified gauge with new data
	'''
    gameDisplay.blit(rpmGaugeImg, (x, y))

def gaugeMPH(x, y):
	'''
	 Function: gaugeMPH()
        Inputs: x,y - Int type values representing gauge location
        Outputs: None
        Usage: Updates specified gauge with new data
	'''
    gameDisplay.blit(speedoGaugeImg, (x, y))

def gaugeTemp(x,y):
	'''
	 Function: gaugeTemp()
        Inputs: x,y - Int type values representing gauge location
        Outputs: None
        Usage: Updates specified gauge with new data
	'''
    gameDisplay.blit(tempGaugeImg, (x, y))

def gaugeGear(x,y):
	'''
	 Function: gaugeGear()
        Inputs: x,y - Int type values representing gauge location
        Outputs: None
        Usage: Updates specified gauge with new data
	'''
    gameDisplay.blit(gearGaugeImg, (x, y))

def rpmCompare(RPM,count):
    rpmSlice = (6400-0) / count
    if RPM is None or RPM == 0 :
        rpmSelection = 0
    else:
        rpmSelection = RPM / rpmSlice
        if rpmSelection > count:
            rpmSelection = count
    return int(round(rpmSelection,0))

def mphCompare(MPH,count):
    mphSlice = (160-0) / count
    if MPH == 0:
        mphSelection = 0
    else:
        mphSelection = MPH / mphSlice
        if mphSelection > count:
            mphSelection = count
    #print(mphSelection)
    return int(round(mphSelection,0))

def coolantCompare(Temp,count):
    #print(Temp)
    Temp = Temp
    coolantSlice = (120-60) / count
    if Temp < 60:
        coolantSelection = 0
    else:
        coolantSelection = (Temp-60) / coolantSlice
        if coolantSelection > count:
            coolantSelection = count
        
        #print(coolantSlice)
    return int(round(coolantSelection,0))

def gearCompare(Gear,count):
    gearSelection = Gear
    return int(round(gearSelection,0))

def fadeSplashOut():
    clock.tick(60)
    time.sleep(2)
    for i in range(100,0,-5):
        splashScreen = pygame.image.load('/home/pi/bluetoothHarness/bluetooth-harness-main/Gauges/Splash/Splash_' + str(i) + '.png')
        splashScreen = pygame.transform.scale(splashScreen,(display_width,display_height))
        gameDisplay.blit(splashScreen, (0, 0))
        pygame.display.update()


        #print("HERE")

def imagePreload(rpmCount,mphCount,coolantCount,gearCount):
    rpmDict = {}
    mphDict = {}
    coolantDict = {}
    gearDict = {}
    for i in range(0,rpmCount+1):
        rpmDict[i] = pygame.image.load(
            "/home/pi/bluetoothHarness/bluetooth-harness-main/Gauges/Gauges_RPM/" + 'RPM_' + str(i) + '.png')
    for i in range(0,mphCount+1):
        mphDict[i] = pygame.image.load(
            "/home/pi/bluetoothHarness/bluetooth-harness-main/Gauges/Gauges_Speedo/" + 'MPH_' + str(i) + '.png')
    for i in range(0,coolantCount+1):
        coolantDict[i] = pygame.image.load(
            "/home/pi/bluetoothHarness/bluetooth-harness-main/Gauges/Gauges_Temp/" + 'Temp_' + str(i) + '.png')
    for i in range(0,gearCount+1):
        gearDict[i] = pygame.image.load(
            "/home/pi/bluetoothHarness/bluetooth-harness-main/Gauges/Gauges_Gear/" + 'Gear_' + str(i) + '.png')

    ImageList = [rpmDict,mphDict,coolantDict,gearDict]
    #print("Finished")
    return ImageList


if __name__ == '__main__':
    pygame.init()
    display_width =1024
    display_height = 600
    global gpsData
    global rpmData
    global tempData
    global gearData

    gpsData = 0
    rpmData = 0
    tempData = 40
    gearData = 0

    gameDisplay = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    #gameDisplay = pygame.display.set_mode((display_width,display_height))
    pygame.display.set_caption('Gauge Cluster')
    splashScreen = pygame.image.load('/home/pi/bluetoothHarness/bluetooth-harness-main/Gauges/Splash/Splash_100.png')
    splashScreen = pygame.transform.scale(splashScreen,(display_width,display_height))
    gameDisplay.blit(splashScreen,(0,0))
    pygame.display.update()
    time.sleep(0.5)
    black = (0, 0, 0)
    white = (255, 255, 255)

    clock = pygame.time.Clock()
    crashed = False

    x = -120
    y = -50

    #gameDisplay

    hostMACAddress = 'E4:5F:01:89:A3:A2'
    imageList = imagePreload(95,88,19,6)

    serverConnectionDict = setupSocketThreads(hostMACAddress,4)
    fadeThread = threading.Thread(target=fadeSplashOut)
    fadeThread.run()
    #imageList = imagePreload(95,88,19,6)


    #print("HELLO")
    
    GPSThread = threading.Thread(target=socketThread, args=(serverConnectionDict[0], 0, 0))
    rpmThread = threading.Thread(target=socketThread,args=(serverConnectionDict[1],1,0))
    tempThread = threading.Thread(target=socketThread, args=(serverConnectionDict[2], 2, 0))
    gearThread = threading.Thread(target=socketThread,args=(serverConnectionDict[3],3,0))

    '''
    tempThread = threading.Thread(target=socketThread, args=(serverConnectionDict[1], 1, 0))
    gearThread = threading.Thread(target=socketThread,args=(serverConnectionDict[2],2,0))
    rpmThread = threading.Thread(target=socketThread,args=(serverConnectionDict[3],3,0))
    '''
    startTime = time.time()
    try:

        while not crashed:
            GPSThread = threading.Thread(target=socketThread, args=(serverConnectionDict[0], 0, 0))
            rpmThread = threading.Thread(target=socketThread,args=(serverConnectionDict[1],1,0))
            tempThread = threading.Thread(target=socketThread,args=(serverConnectionDict[2],2,0))
            gearThread = threading.Thread(target=socketThread,args=(serverConnectionDict[3],3,0))

            A = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    crashed = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        crashed = True
            gameDisplay.fill(black)    

            
            
            GPSThread.run()
            rpmThread.run()
            tempThread.run()
            gearThread.run()
            #print(gpsData)
            #input("Pause Here")
            if gpsData is not None:
                MPH = round((socketParse(gpsData)), 0)
            else:
                MPH = 10
                
            if gearData is not None:
                Gear = round(socketParse(gearData),0)
            else:
                Gear = 0
                
            if rpmData is not None:
                RPM = round(socketParse(rpmData),0)
            else:
                RPM = 2000
                
                
            if tempData is not None:
                coolantTemp = socketParse(tempData)
            else:
                tempData = 86
            '''
            tempThread.run()
            gearThread.run()
            rpmThread.run()
            
            # print(X)
            if tempData is not None:
                coolantTemp = socketParse(tempData) *2
            else:
                tempData = 86
            if gearThread is not None:
                Gear = round(socketParse(gearData),0)
            else:
                Gear = 0
            if rpmThread is not None:
                RPM = round(socketParse(rpmData),0)
            else:
                RPM = 2000
            '''
            #coolantTemp = 85 + 25 * random.random()
            #print(coolantTemp)
            #MPH = 80 + 25 * random.random()
            #RPM = 4000 + 1000 * random.random()
            #Gear = 3 + round(3*random.random(),0)
            rpmImage = rpmCompare(RPM,95)
            mphImage = mphCompare(MPH,88)
            coolantImage = coolantCompare(coolantTemp,19)
            gearImage = gearCompare(Gear,6)


            rpmGaugeImg = imageList[0][rpmImage]
            speedoGaugeImg = imageList[1][mphImage]
            tempGaugeImg = imageList[2][coolantImage]
            gearGaugeImg = imageList[3][gearImage]
            gaugeTemp(x + 380, y + 0)
            gaugeGear(x + 525, y + 275)
            gaugeRPM(x+600, y+25)
            gaugeMPH(x-20,y+25)
            pygame.display.update()
            clock.tick(45)
            #print(time.time() - A)

        pygame.quit()
        
    finally:
	
        #call("sudo shutdown -h now", shell=True)
        pass
 
