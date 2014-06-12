import bee, libcontext
from bee.segments import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

class on_next(bee.worker):
  inp = antenna("push", "trigger")
  outp = output("push", "trigger")
  trig_outp = triggerfunc(outp)
  @modifier
  def do_next(self):
    self.event_next(self.nextevent)  
  trigger(inp, do_next)
  
  def set_event_next(self, event_next):    
    self.event_next = event_next  
  def place(self):
    self.nextevent = ("on_next",self._beename,id(self))
    listener = plugin_single_required(("match", self.trig_outp, self.nextevent))
    libcontext.plugin(("evin", "listener"), listener)

    s = socket_single_required(self.set_event_next) 
    libcontext.socket(("evin","event","next"),s)
