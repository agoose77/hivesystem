import libcontext, bee
from bee.segments import *
from bee.types import stringtupleparser
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class change(object):

    """The change trigger fires every tick if its input is different from the previous tick"""

    metaguiparams = {
        "type_": "str",
        "autocreate": {"type_": "bool"},
    }

    @classmethod
    def form(cls, f):
        f.type_.name = "Type"
        f.type_.type = "option"
        f.type_.options = "bool", "int", "float", "(str,identifier)", "(str,action)", "(str,keycode)", "(str,message)", "(str,property)", "(str,process)", "str", "(object,matrix)", "(object,bge)", "object", "custom"
        f.type_.optiontitles = "Bool", "Integer", "Float", "ID String", "Action String", "Key String", "Message String", "Property String", "Process ID String", "Generic String", "Matrix Object", "BGE Object", "Generic Object", "Custom"
        f.type_.default = "bool"

    def __new__(cls, type_):
        type_ = stringtupleparser(type_)

        class change(bee.worker):
            __doc__ = cls.__doc__

            inp = antenna("pull", type_)
            b_inp = buffer("pull", type_)
            connect(inp, b_inp)

            trig = output("push", "trigger")
            trigfunc = triggerfunc(trig)
            pullfunc = triggerfunc(b_inp)

            # Name the inputs and outputs
            guiparams = {
                "inp": {"name": "Input"},
                "trig": {"name": "Trigger"},
            }

            def update_value(self):
                self.pullfunc()

                if self.previous_state != self.b_inp:
                    self.trigfunc()

                self.previous_state = self.b_inp

            def enable(self):
                # Add a high-priority deactivate() listener on every tick
                self.add_listener("trigger", self.update_value, "tick", priority=9)

            def set_add_listener(self, add_listener):
                self.add_listener = add_listener

            def place(self):
                self.previous_state = None

                libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
                #Make sure we are enabled at startup
                libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))

        return change