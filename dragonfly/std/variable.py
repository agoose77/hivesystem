import bee
from bee.segments import *
from bee.types import typecompare
import bee.segments.variable

class variable(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    class variable(bee.worker):
      inp = antenna("push", type)
      value = bee.segments.variable(type)
      outp = output("pull", type)
      connect(inp, value)
      connect(value, outp)
      guiparams = {"is_variable": True}
      if typecompare(type, "object"):
        parameter(value, None)
      else:
        parameter(value)  
    return variable

variable_str = variable("str")
variable_int = variable("int")
variable_float = variable("float")
variable_bool = variable("bool")
