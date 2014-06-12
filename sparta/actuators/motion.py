import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class motion(bee.worker):
    """
    When triggered, the motion actuator adds the location and rotation to the view matrix
    Modeled on the BGE motion actuator (simple mode)    
    """
        
    #Inputs and outputs
    trig = antenna("push", "trigger")
    view = antenna("pull", ("object", "matrix"))
    location = antenna("pull", "Coordinate")
    rotation = antenna("pull", "Coordinate")
      
    # Mark "object class" as an initially folded, and define the I/O names
    guiparams = {
      "trig" : {"name": "Trigger"},
      "view" : {"name": "View Matrix"},
      "location" : {"name": "Location", "fold" : True},
      "rotation" : {"name": "Location", "fold" : True},
      "_memberorder" : ["trig", "view", "location", "rotation"],
    }
                
    # Finally, declare our sockets and plugins, to communicate with the rest of the hive
    def place(self):    
        raise NotImplementedError("sparta.sensors.motion has not been implemented yet") 
        
      
     