import libcontext, bee
from bee.segments import *


class if_(bee.worker):
    """
    The if processor has a trigger and an input. When it is triggered, it forwards the trigger only if the input is True.
    """

    inp = antenna("pull", "bool")
    b_inp = buffer("pull", "bool")

    trig = antenna("push", "trigger")
    outp = output("push", "trigger")
    trig_outp = triggerfunc(outp)

    # When we receive a trigger:
    # - Update the input
    # - Test the value, and trigger the output if True
    trigger(trig, b_inp)

    @modifier
    def test_inp(self):
        if self.b_inp:
            self.trig_outp()

    trigger(trig, test_inp)

    guiparams = {
        "inp": {"name": "Input"},
        "trig": {"name": "Trigger"},
        "outp": {"name": "Output"},
        "_memberorder": ["inp", "trig", "outp"],
    }
              
      
