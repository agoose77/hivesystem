import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class stop(bee.worker):
    """Stops the current hive. If "delobj" is True, delete any object bound to the hive.
    In case of the top-level hive, this quits the game.
    """
    # Inputs and outputs
    trig = antenna("push", "trigger")
    delobj = variable("bool")
    parameter(delobj, True)

    # Define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
    }

    @classmethod
    def form(self, f):
        f.delobj.name = "Delete object"

    def place(self):
        raise NotImplementedError("sparta.actuators.stop has not been implemented yet") 
      
      
