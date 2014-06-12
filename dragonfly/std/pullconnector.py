import bee
from bee.segments import *

class pullconnector(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    class pullconnector(bee.worker):
      inp = antenna("pull", type)
      outp = output("pull", type)
      connect(inp, outp)
    return pullconnector
