import bee
from bee.segments import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *
class cycle(bee.worker):
  period = antenna("pull", ("float","quantity"))
  b_period = buffer("pull", ("float","quantity"))
  connect(period, b_period)  
  get_period = triggerfunc(b_period, "input")

  value = variable(("float","quantity"))
  startvalue(value, 0)
  parameter(value, 0)

  prev = variable(("float","quantity"))
  startvalue(prev, None)
  
  outp = output("push","trigger")
  trig = triggerfunc(outp)  
  def cycle(self):
    if self.prev is not None: 
      self.value += self.pacemaker.time - self.prev
    self.prev = self.pacemaker.time
    self.get_period()
    if self.b_period > 0:
      while self.value > self.b_period:
        self.value -= self.b_period
        self.trig()
        
  def set_pacemaker(self, pacemaker):
    self.pacemaker = pacemaker
  
  def place(self):
    libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
    libcontext.plugin(("evin","listener"), plugin_single_required(("trigger",self.cycle,"tick")))
