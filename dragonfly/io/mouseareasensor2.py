import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from ._inputsensor import mousesensor_base


class mouseareasensor2(mousesensor_base):
    area = output("push", "id")
    b_area = buffer("push", "id")
    connect(b_area, area)
    trigger_area = triggerfunc(b_area)

    def _send(self, event):
        self.b_area = event[0]
        self.trigger_area()

    def enable(self):
        self.add_listener("leader", self._send, "mousearea")

    def disable(self):
        self.remove_listener("leader", self._send, "mousearea")
