import bee
from bee.segments import *

class pushconnector(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    class pushconnector(bee.worker):
      inp = antenna("push", type)
      outp = output("push", type)
      connect(inp, outp)
    return pushconnector
