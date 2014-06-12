import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class launch(bee.worker):
    """
    The launch actuator launches a new hive process 
    """
    # Inputs and outputs
    trig = antenna("push", "trigger")
    process_class = antenna("pull", ("str", "identifier"))
    process = output("pull", ("str", "process"))

    v_process = variable(("str", "process"))
    connect(v_process, process)

    subprocess = variable("bool")
    parameter(subprocess, True)

    # Mark "object class" as an initially folded, and define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
        "process_class": {"name": "Process class", "fold": True},
        "process": {"name": "Process"},
        "_memberorder": ["trig", "process_class", "process"],
    }

    @classmethod
    def form(cls, f):
        f.subprocess.name = "Subprocess"
        f.subprocess.advanced = True

    def place(self):
        raise NotImplementedError("sparta.actuators.launch has not been implemented yet") 
      
      
