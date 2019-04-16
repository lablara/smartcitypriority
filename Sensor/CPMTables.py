# *********************************************************************
# This is a auxiliary module to manage all configuration tables
# This file is used by Sensor Nodes and the CPM
#
# Author: Daniel G. Costa
#
# *********************************************************************


class NT:
    def __init__(self):
        self.nodes = []
        
    def putNode(self, addr,  a):
        node = Node(addr,  a)
        self.nodes.append(node)
    
    def getNodes (self):
        return self.nodes
        
    def  printValues(self):
        for node in self.nodes:
            print ("Adrress:",  node.getAddress(),  ": a =", node.getApplication())

class Node:
    def __init__(self, ip,  a):
        self.address = ip
        self.application = a
        
    def getApplication (self):
        return self.application
    
    def getAddress (self):
        return self.address
    
class ET:
    def __init__(self, a):
        self.application = a
        self.events = []
    
    def putEvent(self, e, pe):
        event = Event(e, pe)
        self.events.append(event)
    
    def getApplication (self):
        return self.application
    
    def getEvents (self):
        return self.events
    
    def getPe (self):
        return self.Pe
        
    def  printValues(self):
        for event in self.events:
            print ("e =",  event.getE(),  ": Pe =", event.getPe())

class Event:
    def __init__(self, id, p):
        self.e = id
        self.Pe = p
    
    def getE (self):
        return self.e
    
    def getPe (self):
        return self.Pe
    
    
class CT:
    def __init__(self):
        self.contexts = []
    
    def putContext(self, c,  min,  max,  p):
        context = Context(c, min,  max,  p)
        self.contexts.append(context)
    
    def getContexts (self):
        return self.contexts
        
    def printValues(self):
        count = 0
        for context in self.contexts:
            if count != int(context.getContext()):
                count = int(context.getContext())
                print ("Context c =", count)
            print ("R_min =",  context.getRangeMin(), ": R_max =", context.getRangeMax(), ":  Pc = ", context.getPc())

    
class Context:
    def __init__(self, c,  min,  max,  p):
        self.context = c
        self.pc = p
        self.rangeMin = min
        self.rangeMax = max
    
    def getContext (self):
        return self.context
    
    def getPc (self):
        return self.pc
    
    def getRangeMin (self):
        return self.rangeMin

    def getRangeMax (self):
        return self.rangeMax
