import libcontext, bee
from bee.segments import *


class state_activate(bee.worker):

    """The state_activate trigger fires when the hive gets activated by a state change"""

    trig = output("push", "trigger")
    trigfunc = triggerfunc(trig)

    # Name the inputs and outputs
    guiparams = {
        "trig": {"name": "Trigger"},
    }

    def place(self):
        raise NotImplementedError("sparta.triggers.state_activate has not been implemented yet")
    