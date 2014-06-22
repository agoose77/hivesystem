import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class become(bee.worker):
    """
    The become trigger fires every tick if its input has just become True
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

        if not self.previous_state and self.b_inp:
            self.trigfunc()

        self.previous_state = self.b_inp

    def enable(self):
        # Add a high-priority deactivate() listener on every tick
        self.add_listener("trigger", self.update_value, "tick", priority=9)

    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def place(self):
        self.previous_state = False

        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        #Make sure we are enabled at startup
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))