import bee
from bee.segments import *


def fadd(v1, v2):
    return v1.__add__(v2)


class add(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        class add(bee.worker):
            inp1 = antenna("pull", type)
            inp2 = antenna("pull", type)
            outp = output("pull", type)

            w = weaver((type, type), inp1, inp2)
            t = transistor((type, type))
            connect(w, t)
            op = operator(fadd, (type, type), type)
            connect(t, op)
            v_outp = variable(type)
            connect(op, v_outp)
            connect(v_outp, outp)
            pretrigger(v_outp, t)

        return add
