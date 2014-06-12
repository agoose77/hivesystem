import bee
from bee.segments import *

class genfor(bee.worker):
  iterable = antenna("push",("object","iterable"))
  v_iterable = variable(("object","iterable"))       
  connect(iterable, v_iterable)
  
  outp = output("push", "object")  
  b_outp = buffer("push","object")
  connect(b_outp, outp)
  trig_output = triggerfunc(b_outp, "output")

  @modifier
  def iterate(self):
    for v in self.v_iterable:
      self.b_outp = v
      self.trig_output()
  trigger(v_iterable,iterate)
