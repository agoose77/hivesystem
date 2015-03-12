from bee import *
from bee.segments import *
import libcontext


def isnot(test):
    return not test


class filter(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        if type == "trigger":
            class filter(worker):
                inp = Antenna("push", "trigger")
                true = Output("push", "trigger")
                false = Output("push", "trigger")

                filter = Antenna("pull", "bool")
                t_filter = transistor("bool")
                connect(filter, t_filter)
                trigger(inp, t_filter)

                tester = test(t_filter)
                op_isnot = operator(isnot, "bool", "bool")
                connect(t_filter, op_isnot)
                tester_false = test(op_isnot)

                connect(tester, true)
                connect(tester_false, false)
        else:
            class filter(worker):
                inp = Antenna("push", type)

                b = buffer("push", type)
                connect(inp, b)
                true = Output("push", type)
                connect(b, true)

                b_false = buffer("push", type)
                connect(inp, b_false)
                false = Output("push", type)
                connect(b_false, false)

                filter = Antenna("pull", "bool")
                t_filter = transistor("bool")
                connect(filter, t_filter)

                tester = test(t_filter)
                trigger(tester, b)

                op_isnot = operator(isnot, "bool", "bool")
                connect(t_filter, op_isnot)
                tester_false = test(op_isnot)
                trigger(tester_false, b_false)

                trigger(b_false, t_filter, "input")
        return filter
