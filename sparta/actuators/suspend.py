import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class suspend(bee.worker):
    """
    The suspend actuator suspends a hive process
    """
    # Inputs and outputs
    trig = antenna("push", "trigger")
    process = antenna("pull", ("str", "process"))

    b_process = buffer("pull", ("str", "process"))
    connect(process, b_process)
    trigger(trig, b_process)

    @modifier
    def do_suspend(self):
        self.suspend_process(self.b_process)

    trigger(trig, do_suspend)

    # Define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
        "process": {"name": "Process", "fold": True},
        "_memberorder": ["trig", "process"],
    }

    def set_suspend_function(self, supsend_function):
        self.suspend_process = supsend_function

    def place(self):
        libcontext.socket(("process", "suspend"), socket_single_required(self.set_suspend_function))

