import bee, libcontext
from bee.segments import *

class exitactuator(bee.worker):
  inp = antenna("push", "trigger")
  @modifier
  def call_exitfunc(self):
    self.exitfunc()
  trigger(inp, call_exitfunc)  
  def set_exitfunc(self, exitfunc):
    assert hasattr(exitfunc, "__call__")
    self.exitfunc = exitfunc
  def place(self):    
    socketclass = libcontext.socketclasses.socket_single_required
    libcontext.socket("exit", socketclass(self.set_exitfunc))    
  
