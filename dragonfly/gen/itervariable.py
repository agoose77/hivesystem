import bee
from bee.segments import *
import bee.segments.variable


class itervariable(bee.worker):
    v = bee.segments.variable(("object", "iterable"))
    parameter(v)
    outp = output("pull", ("object", "iterable"))
    connect(v, outp)
