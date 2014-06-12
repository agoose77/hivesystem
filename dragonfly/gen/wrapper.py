import bee
from bee.segments import *


class wrapper(bee.worker):
    wrapped = variable(("object", "callable"))
    parameter(wrapped)
    outp = output("pull", "object")
    v_outp = variable("object")
    connect(v_outp, outp)

    @modifier
    def call_wrapped(self):
        self.v_outp = self.wrapped()

    pretrigger(v_outp, call_wrapped)
