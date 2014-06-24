import libcontext, bee
from bee.segments import *


class stop(bee.worker):
    """
    The stop trigger fires when the hive gets stopped
    """

    trig = output("push", "trigger")
    trigfunc = triggerfunc(trig)

    # Name the inputs and outputs
    guiparams = {
        "trig": {"name": "Trigger"},
    }

    def place(self):
        raise NotImplementedError("sparta.triggers.stop has not been implemented yet")
