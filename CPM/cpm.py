#!/usr/bin/env python3

# Code of the CPM module
# Author: Daniel G. Costa

import os
import socket,  pickle
import random
from _thread import *
import threading
import base64
from Crypto import Random
from Crypto.Cipher import AES
from CPMTables import NT, ET, CT  

#Configurations tables
nodes = None
events = []
contexts = None

maximumEvents = 3

#Criptography keys for 3 different "application"
Cr = ['a1cdefghijklmnop','a2cdefghijklmnop', 'a3cdefghijklmnop']

#This thread manages the connections with the nodes 
def threaded(c, address): 
    #Communication follows the definitions in the Article
        
    nodeApplication = 0
    
    #Receiving the value of a
    data = c.recv(1024)
    nodeApplication = int(str(data,  'utf8'))
    print("") 
    print ("Node informed application: a =",  nodeApplication)
    print ("Starting challenge...")    
    
    try:
    
        #Only 3 applications allowed in this implementation
        global maximumEvents
        if nodeApplication > 0 and nodeApplication < (maximumEvents+1):
            #Starting challenge
            numberInitial = str(random.randint(1, 101))
            #padding must be added
            challenge = encrypt(numberInitial,  Cr[nodeApplication-1])
            c.sendall(challenge)
    
            #Wait for the answer from the node
            result = c.recv(1024)
            answer = decrypt(result,  Cr[nodeApplication-1])
            
            #challenge test
            if int(answer) == (int(numberInitial) * int(numberInitial)):
                print ("Changelled was sucessfully answered.")
                insertIntoNodes(address,  nodeApplication)
        
                #Send the ET of the corresponding a
                for event in events:
                    if str(event.getApplication()) == str(nodeApplication):
                        #Send the entire object
                        print ("Sending ET for a =", nodeApplication, "...")
                        tableEt = pickle.dumps(event)
                        c.sendall(tableEt)
        
                msg = str(c.recv(1024), 'utf8')
                if msg == '1':
                    #Send the CT 
                    print ("Sending CT...")
                    tableCt = pickle.dumps(contexts)
                    c.sendall(tableCt)
                    print("Tables ET and CT sucessfully transmitted.")
                else:
                    print("Tables CT could not be transmitted.")
        
            else:
                #Challenge failed
                print ("Node failed the challenge.")
                removeFromNodes(address, nodeApplication)
                c.sendall(bytes('0', 'utf8'))
        else:
            print ("Informed value of a is invalid.")
            removeFromNodes(address, nodeApplication)
       
    except:
            print ("Challenge failed.")
            removeFromNodes(address, nodeApplication)
    
    # connection closed 
    print ("Sensor", address, "disconnected.")
    c.close()

def encrypt(raw,  key):
    iv = Random.new().read( AES.block_size )
    cipher = AES.new(key, AES.MODE_CFB, iv )
    return (base64.b64encode( iv + cipher.encrypt( raw ) ) )

def decrypt(enc,  key):
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(key, AES.MODE_CFB, iv )
    return cipher.decrypt( enc[16:] )
    

#Check if a node is inside the NT. True if it is inside    
def checkNodesTable(addr,  a):
    global nodes
    control = False
    for node in nodes.getNodes():
        if node.getAddress() == addr:
            if node.getApplication() == a:
                control = True
                
    return control

def insertIntoNodes(addr, a):
    global nodes
    control = True
    for node in nodes.getNodes():
        if node.getAddress() == addr:
        	#Update NT
        	node.setApplication(a)
        	control = False

    if control:
    	nodes.putNode(addr, a)
    
    print ("\nUpdated list of registered nodes (NT):")
    nodes.printValues()
    print ("")

    
def removeFromNodes(addr, a):
    global nodes

    for node in nodes.getNodes():
        if node.getAddress() == addr:
        	nodes.removeNode(node)
    
    print ("\nUpdated list of registered nodes (NT):")
    nodes.printValues()
    print ("")


#This method reads all table files and create lists with the informations
def readTables():
    #Nodes table
    global nodes
    nodes = NT()
    
    #Events table
    global events
    global maximumEvents 
    list = os.listdir("tables/events/") # dir is your directory path
    maximumEvents = len(list)
    for n in range(1, maximumEvents+1):
        fileEvents = open ("tables/events/" + str(n) + ".txt",  'r') 
        lines=fileEvents.readlines()
        et = ET(n)  #Create the ET for A=n
        for line in lines:
            #Append each occurance of the event to the application A=n
            et.putEvent (line.strip().split(' ')[0], line.strip().split(' ')[1])
        events.append(et)  #Adds the definition of the Event
        fileEvents.close()
   
    print("All configured Events:")
    for et in events:
        print ("Events for a =", et.getApplication())
        et.printValues()

    #Context table
    global contexts
    fileContext = open ("tables/context.txt",  'r')
    lines=fileContext.readlines()
    contexts = CT()
    for line in lines:
        contexts.putContext (line.strip().split(' ')[0], line.strip().split(' ')[1], line.strip().split(' ')[2], line.strip().split(' ')[3])
    print("\nAll configured Context parameters:")
    contexts.printValues()
    
    fileContext.close()

    print("")

def Main():
    print ("Initializing the CPM...\n")
    
    #Read configuration tables and create the data structures
    readTables()
   
   #Initiate the CPM to receive connections
    host = "" 
    port = 42100
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port)) 
    
    print("CPM is ready and waiting connections at port", port, "...") 
    
    #Put the socket into listening mode 
    s.listen() 

    try:
        while True: 
        
            #Establish connection with client 
            c, addr = s.accept() 
  
            print('\nNew sensor connected:', addr[0], ':', addr[1]) 
  
            #Start a new thread to manage the communication
            start_new_thread(threaded, (c,addr[0])) 
    except:
        print ("CPM is closing...")
        s.shutdown(socket.SHUT_RDWR) 
  
if __name__ == '__main__': 
    Main() 
