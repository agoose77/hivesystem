import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class message(bee.worker):
    """
    The message actuator sends a message to a target process 
    Target process can be empty (sends a message to self)
    It can also be used to send messages the parent, or from one sibling to another, etc.
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
      
      
