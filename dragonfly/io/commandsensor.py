from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class commandsensor(worker):
    outp = output("push", "str")
    b_outp = buffer("push", "str")
    connect(b_outp, outp)
    trig_outp = triggerfunc(b_outp)

    def send_event(self, event):
        self.b_outp = str(event)
        self.trig_outp()

    def place(self):
        libcontext.socket(("evin", ("input", "command")), socket_flag())
        listener = plugin_single_required(("leader", self.send_event, "command"))
        libcontext.plugin(("evin", "listener"), listener)
