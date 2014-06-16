import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class if_(bee.worker):
    """
    The if trigger fires every tick if its input is True
    """

    inp = antenna("pull", "bool")
    b_inp = buffer("pull", "bool")
    connect(inp, b_inp)

    trig = output("push", "trigger")
    trigfunc = triggerfunc(trig)
    pullfunc = triggerfunc(b_inp)

    # Name the inputs and outputs
    guiparams = {
        "inp": {"name": "Input"},
        "trig": {"name": "Trigger"},
    }

    def update_value(self):
        self.pullfunc()

        if self.b_inp:
            self.trigfunc()

    def enable(self):
        # Add a high-priority deactivate() listener on every tick
        self.add_listener("trigger", self.update_value, "tick", priority=9)

    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def place(self):
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        #Make sure we are enabled at startup
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))