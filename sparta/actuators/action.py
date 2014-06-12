import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class action(bee.worker):
    """
    The action actuator plays a 3D action 
    """
    
    #Inputs and outputs
    trig = antenna("push", "trigger")
    action = antenna("pull", ("str", "action"))
    
    # Define the I/O names
    guiparams = {
      "trig" : {"name": "Trigger"},
      "action" : {"name": "Action", "fold": True},
      "_memberorder" : ["trig", "action"],
    }
        
    def place(self):
        raise NotImplementedError("sparta.actuators.action has not been implemented yet") 
      
      
