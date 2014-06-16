# untested

import bee
from bee.segments import *


class trigger_true(bee.worker):
    inp = antenna("push", "trigger")
    outp = output("push", "bool")
    b_outp = buffer("push", "bool")
    startvalue(b_outp, True)
    connect(b_outp, outp)
    trigger(inp, b_outp)
  
