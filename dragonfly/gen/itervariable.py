import bee
from bee.segments import *
import bee.segments.variable


class itervariable(bee.worker):
    variable = bee.segments.variable(("object", "iterable"))
    parameter(variable)
    outp = output("pull", ("object", "iterable"))
    connect(variable, outp)
