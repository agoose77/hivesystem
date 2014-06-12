import libcontext, bee
from bee.segments import *


class toggle(bee.worker):
    """
    The toggle processor toggles its state when triggered
    """

    state = variable("bool")
    parameter(state)
    active = output("pull", "bool")
    connect(state, active)

    # When we receive a trigger, become active
    trig = antenna("push", "trigger")

    @modifier
    def toggle_state(self):
        if self.state:
            self.state = False
        else:
            self.state = True

    trigger(trig, toggle_state)

    # Capitalize the I/O names    
    guiparams = {
        "active": {"name": "Active"},
        "trig": {"name": "Trigger"},
        "_memberorder": ["trig", "active"],
    }

    @classmethod
    def form(cls, f):
        f.state.name = "Initial state"
              
      
