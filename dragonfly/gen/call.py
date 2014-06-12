import bee
from bee.segments import *
import functools
"""
Calls a function with pre-set input argument
Supports the bee.resolve interface
"""
class call(bee.worker):  
  inp = antenna("push","object")
  v_inp = variable("object")
  connect(inp, v_inp)
  func = variable(("object","callable"))
  parameter(func)
  args = variable("object")
  parameter(args, tuple())  
  @modifier
  def call(self):
    if isinstance(self.args, tuple):
      args = self.args + (self.v_inp,)            
    else:
      args = (self.args, self.v_inp)
    args = [bee.resolve(a,self.parent) for a in args]
    if isinstance(self.func, functools.partial):
      self.func(*args)
    else:
      self.func.im_func(*args)
  trigger(v_inp, call)
  
  def set_parent(self, parent):
    self.parent = parent
