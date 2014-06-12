import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class kill(bee.worker):
    """
    The kill actuator kills a hive process 
    """
    #Inputs and outputs
    trig = antenna("push", "trigger")
    process = antenna("pull", ("str", "process"))
    
    # Define the I/O names
    guiparams = {
      "trig" : {"name": "Trigger"},
      "process" : {"name": "Process", "fold": True},
      "_memberorder" : ["trig", "process"],
    }
        
    def place(self):
        raise NotImplementedError("sparta.actuators.kill has not been implemented yet") 
      
      
