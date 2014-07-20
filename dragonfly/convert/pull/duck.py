import bee
from bee.segments import *


class duck(object):
    metaguiparams = {"type1": "type", "type2": "type"}

    def __new__(cls, type1, type2):
        class duck(bee.worker):
            inp = antenna("pull", type1)
            b_inp = buffer("pull", type1)
            connect(inp, b_inp)

            outp = output("pull", type2)
            v_outp = variable(type2)
            connect(v_outp, outp)

            @modifier
            def do_duck(self):
                self.v_outp = self.b_inp

            pretrigger(v_outp, b_inp)
            pretrigger(v_outp, do_duck)

        return duck
