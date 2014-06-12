import libcontext, bee
from bee.segments import *
from bee.types import stringtupleparser


class change(object):
    """
    The change trigger fires every tick if its input is different from the previous tick
    """
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

            # Name the inputs and outputs
            guiparams = {
                "inp": {"name": "Input"},
                "trig": {"name": "Trigger"},
            }

            def place(self):
                raise NotImplementedError("sparta.triggers.change has not been implemented yet")

        return change