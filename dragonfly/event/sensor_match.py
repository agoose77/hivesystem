from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class sensor_match(worker):
    match = variable("event")
    parameter(match)
    outp = output("push", "trigger")
    trig_outp = triggerfunc(outp)

    def place(self):
        listener = plugin_single_required(("match", self.trig_outp, self.match))
        libcontext.plugin(("evin", "listener"), listener)
