import libcontext, bee
from bee.segments import *
from bee.types import stringtupleparser


class hop_out(object):

    """The hop_out rerouter has its output forwarded from a hop_in rerouter of the same name"""

    metaguiparams = {
        "mode": "str",
        "type_": "str",
        "autocreate": {"mode": "pull", "type_": "bool"},
        "_memberorder": ["mode", "type_"]
    }

    @classmethod
    def form(cls, f):
        f.mode.name = "Mode"
        f.mode.type = "option"
        f.mode.options = "push", "pull"
        f.mode.optiontitles = "Push", "Pull"

        f.type_.name = "Type"
        f.type_.type = "option"
        f.type_.options = "bool", "int", "float", "(str,identifier)", "(str,action)", "(str,keycode)", "(str,message)",\
                          "(str,property)", "(str,process)", "str", "(object,matrix)", "(object,bge)", "object", "custom"
        f.type_.optiontitles = "Bool", "Integer", "Float", "ID String", "Action String", "Key String", "Message String",\
                               "Property String", "Process ID String", "Generic String", "Matrix Object", "BGE Object",\
                               "Generic Object", "Custom"
        f.type_.default = "bool"

    def __new__(cls, mode, type_):
        type_ = stringtupleparser(type_)

        class hop_out(bee.worker):
            __doc__ = cls.__doc__

            name_ = variable("str")
            parameter(name_)

            outp = output(mode, type_)
            b_outp = buffer(mode, type_)
            connect(b_outp, outp)
            trig_outp = triggerfunc(b_outp)

            @staticmethod
            def form(f):
                f.name_.name = "Name"

            guiparams = {
                "outp": {"name": "Output"},
            }

            def place(self):
                raise NotImplementedError("sparta.assessors.hop_out is not designed for use outside of the Hive GUI")

        return hop_out
