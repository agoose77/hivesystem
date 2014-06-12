import bee
from bee.segments import *

class equal2(object):
  metaguiparams = {"type":"type"}
  def __new__(cls,type):  
    class equal2(bee.worker):
      v_cmp = variable(type)
      parameter(v_cmp)
      op = operator(type.__eq__,(type,type), "bool")
      inp = antenna("push",type)
      v_inp = variable(type)
      connect(inp, v_inp)
      w = weaver((type,type),v_cmp,v_inp)
      t_w = transistor((type,type))
      connect(w,t_w)
      trigger(v_inp, t_w)
      connect(t_w, op)
      outp = output("push","bool")
      connect(op,outp)    
    return equal2
