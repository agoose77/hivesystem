import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class message(bee.worker):
    """
    The message actuator sends a message to a target process 
    Target process can be empty (sends a message to self)
     It can also be .. to send to the parent, ../sibling to send to a sibling, etc.
    """
    # Inputs and outputs
    trig = antenna("push", "trigger")
    message = antenna("pull", ("str", "message"))
    process = antenna("pull", ("str", "process"))

    # Define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
        "message": {"name": "Message", "fold": True},
        "process": {"name": "Process", "fold": True},
        "_memberorder": ["trig", "message", "process"],
    }

    def place(self):
        raise NotImplementedError("sparta.actuators.message has not been implemented yet") 
      
      
