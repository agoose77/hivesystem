import libcontext, bee
from bee.segments import *

class start(bee.worker):
    """
    The start trigger fires on the first tick (start event)
    """
    
    trig = output("push", "trigger")
    trigfunc = triggerfunc(trig)
        
    # Name the inputs and outputs
    guiparams = {
      "trig" : {"name" : "Trigger"},
    }
    def place(self):
        raise NotImplementedError("sparta.triggers.start has not been implemented yet")
    