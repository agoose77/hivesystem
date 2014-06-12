import libcontext, bee
from bee.segments import *


class state_deactivate(bee.worker):
    """
    The state_deactivate trigger fires when the hive gets deactivated by a state change
    """

    trig = output("push", "trigger")
    trigfunc = triggerfunc(trig)

    # Name the inputs and outputs
    guiparams = {
        "trig": {"name": "Trigger"},
    }

    def place(self):
        raise NotImplementedError("sparta.triggers.state_deactivate has not been implemented yet")
    