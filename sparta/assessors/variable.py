import libcontext, bee
from bee.segments import *
import bee.segments.variable
from bee.types import stringtupleparser


class variable(object):
    """
    The variable holds a single value
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

        class variable(bee.worker):
            __doc__ = cls.__doc__

            # Implementation
            inp = antenna("push", type_)
            value_ = bee.segments.variable(type_)
            outp = output("pull", type_)
            connect(inp, value_)
            connect(value_, outp)
            parameter(value_)

            @staticmethod
            def form(f):
                f.value_.name = "Value"

            guiparams = {
                "inp": {"name": "Input", "advanced": True},
                "outp": {"name": "Output"},
            }

        return variable
    