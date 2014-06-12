import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from ._inputsensor import keyboardsensor_base
from ..keycodes import *
import sys
python2 = (sys.version_info[0] == 2)

class keyboardsensor_trigger(keyboardsensor_base):
  keycode = variable("str")
  parameter(keycode, "SPACE")  
  outp = output("push", "trigger")
  trigger_outp = triggerfunc(outp)
  def _trigger(self, event):
    #ignore event
    self.trigger_outp()
  def place(self):
    if self.keycode not in asciilist:
      libcontext.socket(("evin", ("input", "keyboard", "extended")), socket_flag())
    place = keyboardsensor_base.place
    if python2: place = place.im_func
    place(self)    
  def enable(self):
    self.add_listener("leader", self._trigger, ("keyboard", "keypressed", self.keycode))
  def disable(self):
    self.remove_listener("leader", self._trigger, ("keyboard", "keypressed", self.keycode))
