import libcontext, bee
from bee.segments import *


class always(bee.worker):
    """
    The always trigger fires on all ticks
    Skip: A poll evaluates one tick, then skips the next Skip ticks.
    """

    trig = output("push", "trigger")
    trigfunc = triggerfunc(trig)

    skip = variable("int")
    parameter(skip)

    # Name the inputs and outputs
    guiparams = {
        "trig": {"name": "Trigger"},
    }

    @staticmethod
    def form(f):
        f.skip.name = "Skip"

    def place(self):
        raise NotImplementedError("sparta.triggers.always has not been implemented yet")
