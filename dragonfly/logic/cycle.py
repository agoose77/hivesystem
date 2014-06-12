import bee
from bee.segments import *


class cycle(bee.worker):
    period = antenna("pull", ("int", "count"))
    b_period = buffer("pull", ("int", "count"))
    connect(period, b_period)

    counter = variable(("int", "count"))
    startvalue(counter, 0)
    parameter(counter, 0)

    inp = antenna("push", "trigger")
    outp = output("push", "trigger")
    trig = triggerfunc(outp)

    @modifier
    def m_cycle(self):
        self.counter += 1
        if self.b_period > 0:
            if self.counter >= self.b_period:
                self.counter -= self.b_period
                self.trig()

    trigger(inp, b_period, "input")
    trigger(inp, m_cycle)
