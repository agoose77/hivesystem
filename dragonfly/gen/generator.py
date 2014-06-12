import bee
from bee.segments import *


class generator(bee.worker):
    genfunc = variable(("object", "generator"))
    parameter(genfunc)
    gen = None
    outp = output("pull", "object")
    v_outp = variable("object")
    connect(v_outp, outp)

    @modifier
    def generate(self):
        if self.gen is None:
            self.gen = genfunc()
        self.v_outp = next(self.gen)

    pretrigger(v_outp, generate)
