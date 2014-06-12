import bee
from bee.segments import *

def isnotfunc(v):
  return not v

class isnot(bee.worker):
  inp = antenna("pull","bool")
  v_outp = variable("bool")

  t_isnot = transistor("bool")
  connect(inp, t_isnot)
  op_isnot = operator(isnotfunc, "bool", "bool")
  connect(t_isnot, op_isnot)
  connect(op_isnot, v_outp)
  
  outp = output("pull","bool")
  connect(v_outp, outp)
  pretrigger(v_outp, t_isnot)
