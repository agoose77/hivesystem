import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class message(bee.worker):
    """
    The message sensor reports any messages that were sent to a specific object during the last tick

    """

    # Are we listening for a specific message?
    p_subject = variable(("str", "message"))
    parameter(p_subject, "")

    #Has a message been received during the last tick?
    is_active = variable("bool")
    startvalue(is_active, False)
    active = output("pull", "bool")
    connect(is_active, active)

    #What is the value of the last message?
    # It will be "" if no key has been pressed/released during the last tick
    subject_value = variable(("str", "message"))
    startvalue(subject_value, "")
    subject = output("pull", ("str", "message"))
    connect(subject_value, subject)

    body_value = variable(("str", "message"))
    startvalue(body_value, "")
    body = output("pull", ("str", "message"))
    connect(body_value, body)

    subject_body_pairs = variable(("object", "iterable", ("str", "str")))
    startvalue(subject_body_pairs, "")
    subject_body = output("pull", ("object", "iterable", ("str", "str")))
    connect(subject_body_pairs, subject_body)

    # Mark "message" as an advanced Output segment, and capitalize the I/O names
    guiparams = {
        "subject_body": {"advanced": True, "name": "Subject-Body Pairs"},
        "subject": {"advanced": True, "name": "Subject"},
        "body": {"advanced": True, "name": "Body"},
        "active": {"name": "Active"},
        "_memberorder": ["subject", "body", "active", "subject_body"],
    }

    # Method to manipulate the Parameter form as it appears in the GUI
    @classmethod
    def form(cls, f):
        f.p_subject.name = "Subject"
        f.p_subject.tooltip = "Specific subject to listen for"

    @property
    def process_name(self):
        try:
            return self.get_process_name()

        except AttributeError:
            pass

    def enable(self):
        self.subscribe(self.handle_message, process_name=self.process_name)
        self.add_listener("trigger", self.update, "tick", priority=9)

        self.active_next = False
        self.subject_body_pairs = []

    def handle_message(self, subject, body):
        if subject != self.p_subject and self.p_subject:
            return

        self.subject_value = subject
        self.body_value = body

        self.active_next = True
        self.subject_body_pairs.append((subject, body))

    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def set_get_process_name(self, get_process_name):
        self.get_process_name = get_process_name

    def set_subscribe(self, subscribe):
        self.subscribe = subscribe

    def set_unsubscribe(self, unsubscribe):
        self.unsubscribe = unsubscribe

    def update(self):
        self.is_active, self.active_next = self.active_next, False
        self.subject_body_pairs.clear()

    def on_cleanup(self):
        self.unsubscribe(self.handle_message, self.process_name)

    def place(self):
        libcontext.socket(("process", "bound"), socket_single_optional(self.set_get_process_name))
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        libcontext.socket(("message", "subscribe"), socket_single_required(self.set_subscribe))
        libcontext.socket(("message", "unsubscribe"), socket_single_required(self.set_unsubscribe))

        libcontext.plugin("cleanupfunction", plugin_single_required(self.on_cleanup))

