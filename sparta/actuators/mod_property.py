import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from bee.types import stringtupleparser

import operator


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

            property_name = antenna("pull", ("str", "property"))
            property_name_buffer = buffer("pull", ("str", "property"))
            connect(property_name, property_name_buffer)
            trigger(trig, property_name_buffer)

            modifier_value = antenna("pull", type_)
            modifier_value_buffer = buffer("pull", type_)
            connect(modifier_value, modifier_value_buffer)
            trigger(trig, modifier_value_buffer)

            mode = variable("str")
            parameter(mode, "add")

            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))
                identifier_buffer = buffer("pull", ("str", "identifier"))
                connect(identifier, identifier_buffer)
                trigger(trig, identifier_buffer)

            else:
                @property
                def identifier_buffer(self):
                    return self.get_entity().entityname

            # Name the inputs and outputs
            guiparams = {
                "trig": {"name": "Trigger"},
                "identifier": {"name": "Identifier", "fold": True},
                "property_name": {"name": "Property Name", "fold": True},
                "modifier_value": {"name": "Modification Value", "fold": True},
                "_memberorder": ["trig", "identifier", "property_name", "modifier_value"],
            }

            @classmethod
            def form(cls, f):
                f.mode.name = "Modification mode"
                f.mode.type = "option"
                f.mode.options = "add", "sub", "mul", "div"
                f.mode.optiontitles = "Add", "Subtract", "Multiply", "Divide"
                f.mode.default = "add"

            @modifier
            def modify_property_value(self):
                identifier = self.identifier_buffer
                property_name = self.property_name_buffer
                modifier_value = self.modifier_value_buffer
                property_value = self.get_property(identifier, property_name)

                operation = self.get_operation()
                result = operation(property_value, modifier_value)
                self.set_property(identifier, property_name, result)

            trigger(trig, modify_property_value)

            def get_operation(self):
                mode = self.mode

                if mode == "add":
                    return operator.add

                if mode == "sub":
                    return operator.sub

                if mode == "mul":
                    return operator.mul

                return operator.truediv

            def set_get_property(self, get_property):
                self.get_property = get_property

            def set_set_property(self, set_property):
                self.set_property = set_property

            def set_get_entity(self, get_entity):
                self.get_entity = get_entity

            def place(self):
                if idmode == "bound":
                    libcontext.socket("entity", socket_single_required(self.set_get_entity))

                libcontext.socket(("entity", "set_property"), socket_single_required(self.set_set_property))
                libcontext.socket(("entity", "get_property"), socket_single_required(self.set_get_property))

        return mod_property
