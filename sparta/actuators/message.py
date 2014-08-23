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

    body = antenna("pull", ("str", "message"))
    b_body = buffer("pull", ("str", "message"))
    startvalue(b_body, "")
    connect(body, b_body)

    subject = antenna("pull", ("str", "message"))
    b_subject = buffer("pull", ("str", "message"))
    startvalue(b_subject, "")
    connect(subject, b_subject)

    process = antenna("pull", ("str"))
    b_process = buffer("pull", ("str"))
    startvalue(b_process, "")
    connect(process, b_process)

    trigger(trig, b_subject)
    trigger(trig, b_body)
    trigger(trig, b_process)

    # Define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
        "body": {"name": "Body  ", "fold": True},
        "subject": {"name": "Subject", "fold": True},
        "process": {"name": "Process", "fold": True},
        "_memberorder": ["trig", "subject", "body", "process"],
    }

    @modifier
    def do_message(self):
        target = self.b_process
        body = self.b_body
        subject = self.b_subject

        self.publish_message(target, subject, body)

    trigger(trig, do_message)

    def set_publish_message(self, publish_message):
        self.publish_message = publish_message

    def place(self):
        libcontext.socket(("message", "publish"), socket_single_required(self.set_publish_message))