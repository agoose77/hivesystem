import libcontext, bee
from bee.segments import *
from bee.types import stringtupleparser


class splitter(object):
    """
    The splitter splits push or trigger output into three
    """
    metaguiparams = {
        "type_": "str",
        "autocreate": {"type_": "trigger"},
    }

    @classmethod
    def form(cls, f):
        f.type_.name = "Type"
        f.type_.type = "option"
        f.type_.options = "trigger", "bool", "int", "float", "(str,identifier)", "(str,action)", "(str,keycode)", "(str,message)", "(str,property)", "(str,process)", "str", "(object,matrix)", "(object,bge)", "object", "custom"
        f.type_.optiontitles = "Trigger", "Bool", "Integer", "Float", "ID String", "Action String", "Key String", "Message String", "Property String", "Process ID String", "Generic String", "Matrix Object", "BGE Object", "Generic Object", "Custom"
        f.type_.default = "trigger"

    def __new__(cls, type_):
        type_ = stringtupleparser(type_)

        class splitter(bee.worker):
            __doc__ = cls.__doc__

            # One input value
            inp = antenna("push", type_)
            # Three output values
            outp1 = output("push", type_)
            outp2 = output("push", type_)
            outp3 = output("push", type_)
            connect(inp, outp1)
            connect(inp, outp2)
            connect(inp, outp3)

            guiparams = {
                "inp": {"name": "Input"},
                "outp1": {"name": "Output 1"},
                "outp2": {"name": "Output 2"},
                "outp3": {"name": "Output 3"},
            }

        return splitter
    