# untested

import bee
from bee.segments import *
from bee.types import parse_parameters, get_parameterclass


class cast(object):
    metaguiparams = {"type1": "type", "type2": "type"}

    def __new__(cls, type1, type2):
        def constructor(inp):
            parser = [get_parameterclass(type2)]
            return parse_parameters(parser, [], [inp], {})[0][0]

        class cast(bee.worker):
            inp = antenna("pull", type1)

            outp = output("pull", type2)
            v_outp = variable(type2)
            connect(v_outp, outp)

            op = operator(lambda x: constructor(x), type1, type2)
            t_op = transistor(type1)
            connect(inp, t_op)
            connect(t_op, op)
            connect(op, v_outp)
            pretrigger(v_outp, t_op)

        return cast
