import bee
from bee.segments import *
import bee.segments.transistor

class transistor(bee.worker):
  inp = antenna("pull","object")
  trig = antenna("push","trigger")
  outp = output("push","object")

  tr = transistor("object")
  connect(inp,tr)
  trigger(trig,tr)
  connect(tr,outp)
