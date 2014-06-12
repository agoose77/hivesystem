import bee
from bee.segments import *


class duck(object):
    metaguiparams = {"type1": "type", "type2": "type"}

    def __new__(cls, type1, type2):
        class duck(bee.worker):
            inp = antenna("pull", type1)
            t_inp = transistor(type1)
            connect(inp, t_inp)

            outp = output("pull", type2)
            v_outp = variable(type2)
            connect(v_outp, outp)

            op = operator(lambda x: x, type1, type2)
            connect(t_inp, op)
            connect(op, v_outp)
            pretrigger(v_outp, t_inp)

        return duck
