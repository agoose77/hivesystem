import bee
from bee.segments import *
import bee.segments.transistor

class transistor(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    class transistor(bee.worker):
      inp = antenna("pull", type)
      trig = antenna("push", "trigger")
      t = bee.segments.transistor(type)
      outp = output("push", type)
      connect(inp, t)
      connect(t, outp)
      trigger(trig, t)
    return transistor
      
  

