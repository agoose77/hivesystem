import bee
from bee.segments import *
import bee.segments.variable


class variable(bee.worker):
    v = bee.segments.variable("object")
    parameter(v)
    outp = output("pull", "object")
    connect(v, outp)
