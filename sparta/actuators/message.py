import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class message(bee.worker):
    """
    The message actuator sends a message to a target process 
    Target process can be empty (sends a message to self)
    It can also be used to send messages the parent, or from one sibling to another, etc.
    """
    # Inputs and outputs
    trig = antenna("push", "trigger")

    p_local = variable("bool")
    parameter(p_local, False)

    message = antenna("pull", ("str", "message"))
    b_message = buffer("pull", ("str", "message"))
    startvalue(b_message, "")

    connect(message, b_message)
    trigger(trig, b_message)

    process = antenna("pull", ("str", "process"))
    b_process = buffer("pull", ("str", "process"))
    startvalue(b_process, "")

    connect(process, b_process)
    trigger(trig, b_process)

    # Define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
        "message": {"name": "Message", "fold": True},
        "process": {"name": "Process", "fold": True},
        "_memberorder": ["trig", "message", "process"],
    }

    @modifier
    def do_message(self):
        target = self.b_process
        body = self.b_message
        message_event = bee.event("message", target, body)

        if self.p_local:
            read_event = self.read_local_event
        else:
            read_event = self.read_event

        read_event(message_event)

    trigger(trig, do_message)

    def set_read_event(self, read_event):
        self.read_event = read_event

    def set_read_local_event(self, read_event):
        self.read_local_event = read_event

    def place(self):
        libcontext.socket(("message", "evin"), socket_single_required(self.set_read_event))
        libcontext.socket(("message", "evin"), socket_single_required(self.set_read_local_event))