import libcontext, bee
from bee.segments import *


class switch(bee.worker):

    """The switch processor's state can be triggered on and off"""

    state = variable("bool")
    parameter(state)
    active = output("pull", "bool")
    connect(state, active)

    # When we receive an on trigger, become active
    on_ = antenna("push", "trigger")

    @modifier
    def activate(self):
        self.state = True

    trigger(on_, activate)

    # When we receive an off trigger, become inactive
    off = antenna("push", "trigger")

    @modifier
    def deactivate(self):
        self.state = False

    trigger(off, deactivate)

    # Capitalize the I/O names    
    guiparams = {
        "active": {"name": "Active"},
        "on_": {"name": "On"},
        "off": {"name": "Off"},
        "_memberorder": ["on_", "off", "active"],
    }

    @classmethod
    def form(cls, f):
        f.state.name = "Initial state"
