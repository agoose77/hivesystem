import bee
from bee.segments import *
from bee.types import _parametertypes


class equal2(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        eq = _parametertypes[type][1].__eq__

        class equal2(bee.worker):
            v_cmp = variable(type)
            parameter(v_cmp)
            op = operator(eq, (type, type), "bool")
            inp = antenna("pull", type)
            w = weaver((type, type), v_cmp, inp)
            t_w = transistor((type, type))
            connect(w, t_w)
            connect(t_w, op)
            v_outp = variable("bool")
            connect(op, v_outp)
            pretrigger(v_outp, t_w)
            outp = output("pull", "bool")
            connect(v_outp, outp)

        return equal2
