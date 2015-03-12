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

            # Join together inputs
            w = weaver((type, type), inp1, inp2)
            t = transistor((type, type))
            connect(w, t)

            # Allow operator to trigger
            op = operator(fadd, (type, type), type)
            connect(t, op)

            # Set Output variable
            v_outp = variable(type)
            connect(v_outp, outp)

            # Connect the operator to the variable
            connect(op, v_outp)

            # Trigger transistor before Output
            pretrigger(v_outp, t)

        return add
