from __future__ import absolute_import

import bee
from bee.segments import *
import random as random_module

class choice(bee.worker):
  inp = antenna("pull",("object","iterable"))
  b_inp = buffer("pull",("object","iterable"))
  connect(inp,b_inp)
  get_inp = triggerfunc(b_inp, "update")
  
  outp = output("pull","object")
  v_outp = variable("object")
  connect(v_outp,outp)    
  @modifier
  def m_choice(self):
    self.get_inp()
    self.v_outp = random_module.choice(self.b_inp)
  pretrigger(v_outp,m_choice)
