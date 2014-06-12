import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class message(object):
    """
    The message sensor reports any messages that were sent to a specific object during the last tick
    
    """
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


            # Method to manipulate the parameter form as it appears in the GUI
            @classmethod
            def form(cls, f):
                f.p_message.name = "Message"
                f.p_message.tooltip = "Specific message to listen for"


            def place(self):
                raise NotImplementedError("sparta.sensors.message has not been implemented yet")

        return message
        
      
      
