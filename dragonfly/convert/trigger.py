import bee
from bee.segments import *
import bee.segments.trigger


class trigger(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        class trigger(bee.worker):
            inp = antenna("push", type)
            v = buffer("push", type)
            connect(inp, v)
            outp = output("push", "trigger")
            bee.segments.trigger(v, outp)

        return trigger
