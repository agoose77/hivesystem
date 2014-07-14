import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class always(bee.worker):

    """The always trigger fires on all ticks.

    Skip: A poll evaluates one tick, then skips the next Skip ticks
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

    def update_value(self):
        if not self.pacemaker.ticks % (self.skip + 1):
            self.trigfunc()

    def enable(self):
        # Add a high-priority deactivate() listener on every tick
        self.add_listener("trigger", self.update_value, "tick", priority=9)

    def set_pacemaker(self, pacemaker):
        self.pacemaker = pacemaker

    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def place(self):
        libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        #Make sure we are enabled at startup
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))

