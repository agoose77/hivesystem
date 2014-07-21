import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class message(object):

    """The message sensor reports any messages that were sent to a specific object during the last tick"""

    metaguiparams = {
        "idmode": "str",
        "autocreate": {"idmode": "bound"},
    }

    @classmethod
    def form(cls, f):
        f.idmode.name = "ID mode"
        f.idmode.advanced = True
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound"
        f.idmode.default = "bound"
        f.idmode.optiontitles = "Unbound", "Bound"

    def __new__(cls, idmode):
        assert idmode in ("bound", "unbound"), idmode

        class message(bee.worker):
            __doc__ = cls.__doc__

            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))
                identifier_buffer = buffer("pull", ("str", "identifier"))
                connect(identifier, identifier_buffer)
                trigger_identifier_buffer = triggerfunc(identifier_buffer)

                @property
                def process_name(self):
                    self.trigger_identifier_buffer()
                    return self.identifier_buffer

            else:
                @property
                def process_name(self):
                    return self.get_process_id()

            # Are we listening for a specific message?
            p_message = variable(("str", "message"))
            parameter(p_message, "")

            #Has a message been received during the last tick?
            is_active = variable("bool")
            startvalue(is_active, False)
            active = output("pull", "bool")
            connect(is_active, active)

            #What is the value of the last message? 
            # It will be "" if no key has been pressed/released during the last tick
            messagevalue = variable(("str", "message"))
            startvalue(messagevalue, "")
            message = output("pull", ("str", "message"))
            connect(messagevalue, message)

            # Mark "message" as an advanced output segment, and capitalize the I/O names
            guiparams = {
                "message": {"advanced": True, "name": "Message"},
                "active": {"name": "Active"},
                "_memberorder": ["message", "active"],
            }

            def update(self):
                self.is_active = self.is_active_next
                self.messagevalue = self.message_value_next
                self.is_active_next = False
                self.message_value_next = ""

            def check_message(self, event):
                # If the leader didn't match and the event is specific
                if event[0] and event.match_leader(self.process_name) is None:
                    return

                message = event[1:]

                if self.p_message:
                    if message != self.p_message:
                        return

                self.message_value_next = message
                self.is_active_next = True


            # Method to manipulate the parameter form as it appears in the GUI
            @classmethod
            def form(cls, f):
                f.p_message.name = "Message"
                f.p_message.tooltip = "Specific message to listen for"

            def set_get_process_id(self, get_process_id):
                self.get_process_id = get_process_id

            #Add event listeners at startup
            def set_add_listener(self, add_listener):
                self.add_listener = add_listener

            def enable(self):
                self.add_listener("trigger", self.update, "tick", priority=9)
                self.add_listener("leader", self.check_message, "message", priority=10)

                self.is_active_next = False
                self.message_value_next = ""

            def place(self):
                #Grab the hive's function for adding listeners
                libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
                #Make sure we are enabled at startup
                libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))

                if idmode == "bound":
                    libcontext.socket(("process", "bound"), socket_single_required(self.set_get_process_id))

        return message