import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from ._inputsensor import mousesensor_base


class mouseareasensor(mousesensor_base):
    area = variable("id")
    parameter(area)
    outp = output("push", "trigger")
    trigger_outp = triggerfunc(outp)

    def _trigger(self, event):
        # ignore event
        self.trigger_outp()

    def enable(self):
        self.add_listener("leader", self._trigger, ("mousearea", self.area))

    def disable(self):
        self.remove_listener("leader", self._trigger, ("mousearea", self.area))
