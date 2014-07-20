import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class resume(bee.worker):
    """
    The resume actuator resumes a suspended hive process
    """
    # Inputs and outputs
    trig = antenna("push", "trigger")
    process = antenna("pull", ("str", "process"))

    b_process = buffer("pull", ("str", "process"))
    connect(process, b_process)
    trigger(trig, b_process)

    @modifier
    def do_resume(self):
        self.resume_function(self.b_process)

    trigger(trig, do_resume)

    # Define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
        "process": {"name": "Process", "fold": True},
        "_memberorder": ["trig", "process"],
    }

    def set_resume_function(self, resume_function):
        self.resume_function = resume_function

    def place(self):
        libcontext.socket(("process", "resume"), socket_single_required(self.set_resume_function))


