import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class messagehandler(bee.drone):

    """Manages bound process instances"""

    def __init__(self):
        self._registered_stop_processes = {}

    def set_read_event(self, read_event):
        self.read_event = read_event

    def place(self):
        #libcontext.plugin(("process", "register", "stop"), plugin_supplier(self.register_stop_process))
        libcontext.socket(("evin", "event"), socket_single_required(self.set_read_event))
        libcontext.plugin(("message", "evin"),
                          plugin_supplier(lambda *args, **kwargs: self.read_event(*args, **kwargs)))

      #  libcontext.plugin("cleanupfunction", plugin_single_required(self.stop_all_processes))
