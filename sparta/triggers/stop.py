import libcontext, bee
from libcontext.pluginclasses import *
from bee.segments import *


class stop(bee.worker):
    """The stop trigger fires when the hive gets stopped"""

    trig = output("push", "trigger")
    trigfunc = triggerfunc(trig)

    # Name the inputs and outputs
    guiparams = {
        "trig": {"name": "Trigger"},
    }

    def place(self):
        listener = plugin_single_required(("trigger", self.trigfunc, "stop"))
        libcontext.plugin(("evin", "listener"), listener)

