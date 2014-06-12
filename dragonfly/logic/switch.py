from bee import *
from bee.segments import *
import libcontext


class switch(worker):
    true = antenna("push", "trigger")
    false = antenna("push", "trigger")

    state = variable("bool")
    parameter(state, False)

    on = output("pull", "bool")
    connect(state, on)

    outp = output("push", "bool")
    t_outp = transistor("bool")
    connect(state, t_outp)
    connect(t_outp, outp)
    trig_outp = triggerfunc(t_outp)

    @modifier
    def do_true(self):
        if self.state: return
        self.state = True
        self.trig_outp()

    trigger(true, do_true)

    @modifier
    def do_false(self):
        if not self.state: return
        self.state = False
        self.trig_outp()

    trigger(false, do_false)

