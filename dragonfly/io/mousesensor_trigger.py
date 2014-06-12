import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from ._inputsensor import mousesensor_base

class mousesensor_trigger(mousesensor_base):
  mousebutton = variable("str")
  parameter(mousebutton, "LEFT")
  outp = output("push", "trigger")
  trigger_outp = triggerfunc(outp)
  def _trigger(self, event):
    #ignore event
    self.trigger_outp()
  def enable(self):
    self.add_listener("leader", self._trigger, ("mouse", "buttonpressed", self.mousebutton))
  def disable(self):
    self.remove_listener("leader", self._trigger, ("mouse", "buttonpressed", self.mousebutton))
