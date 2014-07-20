# UNTESTED

import bee
from bee.segments import *


def do_join00(v1, v2):
    return (v1, v2)


def do_join10(v1, v2):
    return v1 + (v2,)


def do_join01(v1, v2):
    return (v1,) + v2


def do_join11(v1, v2):
    return v1 + v2


class join(object):
    metaguiparams = {"type1": "type", "type2": "type"}

    def __new__(cls, type1, type2):
        if not isinstance(type1, str) and not isinstance(type1, tuple):
            raise AssertionError("Join type 1 must be tuple, not '%s'" % type(type1))
        
        typetuple1 = type1
        if isinstance(type1, str): typetuple1 = (type1,)

        if not isinstance(type2, str) and not isinstance(type2, tuple):
            raise AssertionError("Join type 2 must be tuple, not '%s'" % type(type2))
        typetuple2 = type2
        if isinstance(type2, str): typetuple2 = (type2,)

        outtype = typetuple1 + typetuple2

        if isinstance(type1, str):
            if isinstance(type2, str):
                f = do_join00
            else:
                f = do_join01
        else:
            if isinstance(type2, str):
                f = do_join10
            else:
                f = do_join11

        class join(bee.worker):
            inp1 = antenna("pull", type1)
            inp2 = antenna("pull", type2)
            w = weaver((type1, type2), inp1, inp2)
            t = transistor((type1, type2))
            connect(w, t)
            o = operator(f, (type1, type2), outtype)
            connect(t, o)
            v_outp = variable(outtype)
            connect(o, v_outp)
            outp = output("pull", outtype)
            connect(v_outp, outp)
            pretrigger(v_outp, t)

        return join
      
  

