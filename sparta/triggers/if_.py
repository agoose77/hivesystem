import libcontext, bee
from bee.segments import *


class if_(bee.worker):
    """
    The if trigger fires every tick if its input is True
    """

    inp = antenna("pull", "bool")
    b_inp = buffer("pull", "bool")
    connect(inp, b_inp)

    trig = output("push", "trigger")
    trigfunc = triggerfunc(trig)

    # Name the inputs and outputs
    guiparams = {
        "inp": {"name": "Input"},
        "trig": {"name": "Trigger"},
    }

    def place(self):
        raise NotImplementedError("sparta.triggers.if_ has not been implemented yet")
    