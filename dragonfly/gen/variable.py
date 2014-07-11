import bee
from bee.segments import *
import bee.segments.variable as segment_variable


class variable(bee.worker):
    value = segment_variable("object")
    parameter(value)
    outp = output("pull", "object")
    connect(value, outp)