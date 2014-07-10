import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class kill(bee.worker):
    """The kill actuator kills a hive process"""
    # Inputs and outputs
    trig = antenna("push", "trigger")
    process = antenna("pull", ("str", "process"))

    b_process = buffer("pull", ("str", "process"))
    connect(process, b_process)
    trigger(trig, b_process)

    @modifier
    def do_kill(self):
        self.delete_function(self.b_process)

    trigger(trig, do_kill)

    # Define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
        "process": {"name": "Process", "fold": True},
        "_memberorder": ["trig", "process"],
    }

    def set_delete_function(self, delete_function):
        self.delete_function = delete_function

    def place(self):
        libcontext.socket(("process", "stop"), socket_single_required(self.set_delete_function))



