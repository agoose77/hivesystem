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
        "trig": {"name": "Trigger"},
    }

    def place(self):
        listener = plugin_single_required(("trigger", self.trigfunc, "start"))
        libcontext.plugin(("evin", "listener"), listener)
