import bee
from bee.segments import *
import bee.segments.buffer


class buffer(object):
    metaguiparams = {"mode": "str", "type": "type"}

    def __new__(cls, mode, type):
        assert mode in ("push", "pull"), mode

        class buffer(bee.worker):
            inp = antenna(mode, type)
            value = bee.segments.buffer(mode, type)
            outp = output(mode, type)
            connect(inp, value)
            connect(value, outp)
            trig = antenna("push", "trigger")
            trigger(trig, value)
            parameter(value)

        return buffer

