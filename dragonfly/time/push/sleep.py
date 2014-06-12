import bee
from bee.segments import *
import time


class sleep(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        class sleep(bee.worker):
            inp = antenna("push", type)
            outp = output("push", type)

            delay = antenna("pull", ("float", "quantity"))
            v_delay = buffer("pull", ("float", "quantity"))
            get_delay = triggerfunc(v_delay)
            connect(delay, v_delay)

            @modifier
            def do_sleep(self):
                self.get_delay()
                time.sleep(self.v_delay)

            if type != "trigger":

                b = buffer("push", type)
                connect(inp, p)
                connect(b, outp)

                trigger(b, do_sleep, "input")
                trigger(b, b, "input", "output")
            else:
                trigger(inp, do_sleep)
                trigger(inp, outp)

        return sleep
         
