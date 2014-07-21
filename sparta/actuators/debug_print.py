import libcontext, bee
from bee.segments import *


class debug_print(bee.worker):
    """The set_property actuator modifies a named property"""

    trig = antenna("push", "trigger")
    message_ = antenna("pull", "str")
    message_default = buffer("pull", "str")
    startvalue(message_default, "Triggered!")
    connect(message_, message_default)

    trigger(trig, message_default)

    # Name the inputs and outputs
    guiparams = {
        "trig": {"name": "Trigger"},
        "message_": {"name": "Message"},
        "_memberorder": ["trig", "message_"],
    }

    @modifier
    def on_triggered(self):
        print(self.message_default)

    trigger(trig, on_triggered)

