from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class sensor_leader(worker):
    leader = variable("event")
    Parameter(leader)
    outp = Output("push", "event")
    b_outp = buffer("push", "event")
    connect(b_outp, outp)
    trig_outp = triggerfunc(b_outp)

    def send_event(self, event):
        self.b_outp = event
        self.trig_outp()

    def place(self):
        listener = plugin_single_required(("leader", self.send_event, self.leader))
        libcontext.plugin(("evin", "listener"), listener)
