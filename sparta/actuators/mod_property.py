import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from bee.types import stringtupleparser


class mod_property(object):
    """
The mod_property actuator modifies a named property
    """
    metaguiparams = {
        "type_": "str",
        "idmode": "str",
        "autocreate": {"idmode": "bound", "type_": "float"},
        "_memberorder": ["idmode", "type_"]
    }

    @classmethod
    def form(cls, f):
        f.idmode.name = "ID mode"
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound", "fallback"
        f.idmode.optiontitles = "Unbound", "Bound", "Fallback"
        f.idmode.default = "bound"

        f.type_.name = "Type"
        f.type_.type = "option"
        f.type_.options = "bool", "int", "float", "(str,identifier)", "(str,action)", "(str,keycode)", "(str,message)", "(str,property)", "(str,process)", "str", "(object,matrix)", "(object,bge)", "object", "custom"
        f.type_.optiontitles = "Bool", "Integer", "Float", "ID String", "Action String", "Key String", "Message String", "Property String", "Process ID String", "Generic String", "Matrix Object", "BGE Object", "Generic Object", "Custom"
        f.type_.default = "float"

    def __new__(cls, idmode, type_):
        assert idmode in ("bound", "unbound", "fallback"), idmode
        type_ = stringtupleparser(type_)

        class mod_property(bee.worker):
            __doc__ = cls.__doc__
            trig = antenna("push", "trigger")
            prop = antenna("pull", ("str", "property"))
            modval = antenna("pull", type_)

            mode = variable("str")
            parameter(mode, "add")

            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))

            # Name the inputs and outputs
            guiparams = {
                "trig": {"name": "Trigger"},
                "identifier": {"name": "Identifier", "fold": True},
                "prop": {"name": "Property Name", "fold": True},
                "modval": {"name": "Modification Value", "fold": True},
                "_memberorder": ["trig", "identifier", "prop", "modval"],
            }

            @classmethod
            def form(cls, f):
                f.mode.name = "Modification mode"
                f.mode.type = "option"
                f.mode.options = "add", "sub", "mul", "div"
                f.mode.optiontitles = "Add", "Subtract", "Multiply", "Divide"
                f.mode.default = "add"

            def place(self):
                raise NotImplementedError("sparta.assessors.mod_property has not been implemented yet")

        return mod_property
