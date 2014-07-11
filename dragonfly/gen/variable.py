import bee
from bee.segments import *
import bee.segments.variable as segment_variable


class variable(bee.worker):
    v = segment_variable("object")
    parameter(v)
    outp = output("pull", "object")
    connect(v, outp)