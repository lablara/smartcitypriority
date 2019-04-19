#!/usr/bin/env python3

# *********************************************************************
# This is a Temperature Sensor
# It is intented to compute a priority index based on the methodology
# of the paper "A Prioritization Approach for Optimization of Multiple
# Concurrent Sensing Applications in Smart Cities"
# Author      : Daniel G. Costa
# E-mail      : danielgcosta@uefs.br
# Date        : 2019/04/01
# *********************************************************************

#Basic modules
from gpiozero import LED, Button
from time import sleep
import datetime
import signal
import threading
import atexit
import socket, pickle
import base64
from Crypto import Random
from Crypto.Cipher import AES

#Sensor and display hardware
import Adafruit_DHT #DHT22 sensor
from prioritydisplay import TM1367

#Desgined module
from CPMTables import ET,CT

#########################################################


#Variables and constants
application = 0  #initial value of "application"
Pmin = 1  
priority = Pmin
fe = 1.0
fc = 1.0
#Criptography key
Cr = 'a1cdefghijklmnop' # a=1
#Cr = 'a2cdefghijklmnop' a=2
#Cr = 'a3cdefghijklmnop' a=3

#temperature threshold
threshold = 40

#Tables to be received from the CPM
eventTable = None
contextTable = None

#GPIO pins
pin1 = 17 #Led for a=1
pin2 = 18 #Led for a=2
pin3 = 21 #Led for a=3 
pin4 = 22 #Led when temperature is higher than the threshold
pin5 = 23 #Button to select the value of a
pin6 = 24 #DHT data pin
pin7 = 25 #TM1367 CLK
pin8 = 4  #TM1367 DIO

#Hardware configurations
yellowLed = LED (pin1)
blueLed = LED (pin2)
greenLed = LED (pin3)
tempLed = LED (pin4)
button = Button (pin5)

#Initiliaze display: CLK and DIO
display = TM1367(pin7,pin8)

#Sensor unit
sensor = Adafruit_DHT.DHT22

#Communication definitions
address = "192.168.0.1" #CPM address
port = 42100


##################################################


#temperature sensor reading
class tempThread (threading.Thread):
    global threshold

    def __init__(self):
        threading.Thread.__init__(self)
      
    def run(self):
        while True:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin6)
            #print (temperature)
            
            if temperature >= threshold:                
                tempLed.on()
                computePriority()                    
        
            else:                
                tempLed.off()
                showPriority(0) #reset priority
                                    
            sleep (2)  #time between temperature readings


#Compute the value of Pf, according to the received tables
#If ET and CT are not receievd, priority is not computed            
def computePriority():

    global eventTable
    global contextTable

    Pe = 0
    if eventTable != None:
        for event in eventTable.getEvents():
            if event.getE() == '1': #only event e=1 is modelled in the tempsensor
                Pe = int(event.getPe())

    Pc = 0
    if contextTable != None:
        today = datetime.datetime.today().weekday() #Monday = 0, Sunday = 6    
        for context in contextTable.getContexts():
            if context.getContext() == '1':
                if int(context.getRangeMin()) <= (today+1) and (today+1) <= int(context.getRangeMax()):
                    Pc = int(context.getPc())
    
    Pf = int(Pe * fe + Pc * fc) #convert to integer
    showPriority (Pf)
    

#Communication with the CPM
def getTablesCPM():
    global address, port, application
    global eventTable, contextTable
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((address, port))
        print ("\nConnection established to the CPM.")
    except:
        print ("The CPM could not be contacted")
        return

    #Send the value of a
    print ("Sending the value of \"a\" to the CPM.","a =",application)
    s.send(bytes(str(application), 'utf8'))

    #Waits for the answer of the CPM. Challenge to be answered
    clg = s.recv(1024)
    challenge = decrypt(clg, Cr)
    
    try:
        challenge = int(challenge)

        if challenge != 0:
            #Sends the answer back to the CPM
            number = challenge * challenge            
            answer = encrypt(str(number), Cr)            
            s.sendall(answer)

            #Waiting for the ET table
            msg = s.recv(4096)

            #If '0' is sent, it is a single byte. Else, it is the table
            if len(msg) > 1:        
                #Node can receive the ET
                print ("Node authentication succeed.")
                print ("Receiving Event Table (ET):")        
                eventTable = pickle.loads(msg)
                eventTable.printValues()
    
                #Wainting for CT Table
                s.send(bytes('1', 'utf8'))

                #Receiving CT table
                print ("Receiving Context Table (CT):")
                msg = s.recv(4096)
                contextTable = pickle.loads(msg)
                contextTable.printValues()

                print ("Tables received")
            else:
                print ("Node is not registered for this application. Connection closed.")
                eventTable = None
                contextTable = None
        else:
            print ("Application is not registered")
            eventTable = None
            contextTable = None
    
    except:
        print ("Authentication failed")
        eventTable = None
        contextTable = None

    print ("Closing connection to the CPM...")
    sleep(1)
    s.close() 


#Encryption method. Used for the "challenge protocol"
def encrypt(raw, key):
    iv = Random.new().read( AES.block_size )
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return (base64.b64encode( iv + cipher.encrypt( raw ) ) )


#Decryption method. Used for the "challenge protocol"
def decrypt(enc, key):
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(key, AES.MODE_CFB, iv )
    return cipher.decrypt( enc[16:] )


#Method called when button is pressed
def changeApplication ():
    global application    

    if application == 3:
        application = 1
    else:
        application += 1
        
    turnonLeds (application)    

    #Get Tables from the CPM
    getTablesCPM()    


#Auxiliary method to control the leds
def turnonLeds (app):
    if app == 1:
        yellowLed.on()
        blueLed.off()
        greenLed.off()

    elif app == 2:
        yellowLed.off()
        blueLed.on()
        greenLed.off()

    elif app == 3:
        yellowLed.off()
        blueLed.off()
        greenLed.on()

    elif app == 0:  #When program exits
        yellowLed.off()
        blueLed.off()
        greenLed.off()
        tempLed.off()
        showPriority(0)


#Sends an integer number to the display module
def showPriority(pri):
    global display
    display.show_priority(pri)


#Called when program exits
def exit_handler():
    global display
    turnonLeds(0)
    display.clearDisplay()
    print ("Temperature sensor is exiting...")
    
    
#Main code of the sensor
###########################3
        
def main():

    print ("Temmperature sensor is initiating...")
    turnonLeds(0) # reset LEDs and display
    
    #initialize the sensor
    global application    
    changeApplication() #first interaction when sensor is turned on    
    button.when_pressed = changeApplication

    #Initialize thread to read temperature from DHT22 sensor
    threadTemp = tempThread()
    threadTemp.start()
    
    atexit.register(exit_handler)

if __name__ == '__main__':
    main()


