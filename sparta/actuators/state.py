import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class state(bee.worker):
    """
    The state actuator changes the state of the current hive 
    """
    
    #Inputs and outputs
    trig = antenna("push", "trigger")
    state = antenna("pull", "str")
    
    # Define the I/O names
    guiparams = {
      "trig" : {"name": "Trigger"},
      "state" : {"name": "State", "fold": True},
      "_memberorder" : ["trig", "state"],
    }
        
    def place(self):
        raise NotImplementedError("sparta.actuators.state has not been implemented yet") 
      
      
