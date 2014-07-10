import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class pause(bee.worker):
    """
    The pause actuator pauses a hive process 
    """
    # Inputs and outputs
    trig = antenna("push", "trigger")
    process = antenna("pull", ("str", "process"))

    b_process = buffer("pull", ("str", "process"))
    connect(process, b_process)
    trigger(trig, b_process)

    @modifier
    def do_pause(self):
        self.pause_function(self.b_process)

    trigger(trig, do_pause)

    # Define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
        "process": {"name": "Process", "fold": True},
        "_memberorder": ["trig", "process"],
    }

    def set_pause_function(self, pause_function):
        self.pause_function = pause_function

    def place(self):
        libcontext.socket(("process", "pause"), socket_single_required(self.set_pause_function))

