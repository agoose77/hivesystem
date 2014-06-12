from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class sensor_all(worker):
    def place(self):
        l = ("all", self.send_event)
        libcontext.plugin(("evin", "listener"), plugin_single_required(l))
