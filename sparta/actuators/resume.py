import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class resume(bee.worker):
    """
    The resume actuator resumes a paused hive process 
    """
    # Inputs and outputs
    trig = antenna("push", "trigger")
    process = antenna("pull", ("str", "process"))

    # Define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
        "process": {"name": "Process", "fold": True},
        "_memberorder": ["trig", "process"],
    }

    def place(self):
        raise NotImplementedError("sparta.actuators.resume has not been implemented yet") 
      
      
