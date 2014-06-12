import bee
from bee.segments import *


class toggle(bee.worker):
    inp = antenna("push", "trigger")
    on = variable("bool")
    parameter(on, False)
    state = output("pull", "bool")
    connect(on, state)

    true = output("push", "trigger")
    trig_true = triggerfunc(true)
    false = output("push", "trigger")
    trig_false = triggerfunc(false)

    @modifier
    def m_trig(self):
        if self.on:
            self.on = False
            self.trig_false()
        else:
            self.on = True
            self.trig_true()

    trigger(inp, m_trig)