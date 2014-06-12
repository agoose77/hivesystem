#untested

import bee
from bee.segments import *
from bee.types import parse_parameters, get_parameterclass

class cast(object):
  metaguiparams = {"type1":"type","type2":"type"}
  def __new__(cls, type1, type2):
    def constructor(inp):
      parser = [get_parameterclass(type2)]
      return parse_parameters(parser,[],[inp],{})[0][0]
    class cast(bee.worker):
      inp = antenna("push",type1)    
      outp = output("push",type2)
      op = operator(lambda x: constructor(x), type1, type2)
      connect(inp, op)
      connect(op,outp)
    return cast
