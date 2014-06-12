import bee
from bee.segments import *

import bee.segments.test


def isnotfunc(v):
    return not v


class test2(bee.worker):
    inp = antenna("pull", "bool")
    test = antenna("push", "trigger")
    outp_if = output("push", "trigger")
    outp_else = output("push", "trigger")

    t_inp = transistor("bool")
    connect(inp, t_inp)
    trigger(test, t_inp)
    subtest = bee.segments.test(t_inp)
    connect(subtest, outp_if)

    isnot = operator(isnotfunc, "bool", "bool")
    connect(t_inp, isnot)
    subtest2 = bee.segments.test(isnot)
    connect(subtest2, outp_else)
