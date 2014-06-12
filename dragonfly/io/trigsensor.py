import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class trigsensor(bee.worker):
  header = variable("str")
  parameter(header)    
  inp = antenna("push", "trigger")
  @modifier
  def display(self):
    self.displayfunc(self.header)
  trigger(inp, display)
  def set_display(self, displayfunc):
    self.displayfunc = displayfunc
  def place(self):
    libcontext.socket("display", socket_single_required(self.set_display))
