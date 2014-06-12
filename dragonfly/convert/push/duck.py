# untested

import bee
from bee.segments import *


class duck(object):
    metaguiparams = {"type1": "type", "type2": "type"}

    def __new__(cls, type1, type2):
        class duck(bee.worker):
            inp = antenna("push", type1)
            outp = output("push", type2)
            op = operator(lambda x: x, type1, type2)
            connect(inp, op)
            connect(op, outp)

        return duck
