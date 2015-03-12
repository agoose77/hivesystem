from bee import *
from bee.segments import *
import libcontext


class switch(worker):
    true = Antenna("push", "trigger")
    false = Antenna("push", "trigger")

    state = variable("bool")
    Parameter(state, False)

    on = Output("pull", "bool")
    connect(state, on)

    outp = Output("push", "bool")
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

