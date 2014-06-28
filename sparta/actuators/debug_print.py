import libcontext, bee
from bee.segments import *


class debug_print(bee.worker):
    """The set_property actuator modifies a named property"""

    trig = antenna("push", "trigger")
    message_default = variable("str")
    parameter(message_default, "Triggered!")

    # Name the inputs and outputs
    guiparams = {
        "trig": {"name": "Trigger"},
        "_memberorder": ["trig"],
    }

    @modifier
    def on_triggered(self):
        print(self.message_default)

    trigger(trig, on_triggered)

    def place(self):
        pass

