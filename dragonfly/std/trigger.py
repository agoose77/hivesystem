import bee
from bee.segments import *

class trigger(bee.worker):
  outp = output("push", "trigger")
  trigger = triggerfunc(outp)
