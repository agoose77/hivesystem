import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from bee.types import stringtupleparser


class set_property(object):
    """
The set_property actuator modifies a named property
    """
    metaguiparams = {
        "type_": "str",
        "idmode": "str",
        "autocreate": {"idmode": "bound", "type_": "bool"},
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
        f.type_.default = "bool"

    def __new__(cls, idmode, type_):
        assert idmode in ("bound", "unbound", "fallback"), idmode
        type_ = stringtupleparser(type_)

        class set_property(bee.worker):
            __doc__ = cls.__doc__
            trig = antenna("push", "trigger")
            property_name = antenna("pull", ("str", "property"))
            property_name_buffer = buffer("pull", ("str", "property"))
            connect(property_name, property_name_buffer)

            property_value = antenna("pull", type_)
            property_value_buffer = buffer("pull", type_)
            connect(property_value, property_value_buffer)

            trigger(trig, property_name_buffer)
            trigger(trig, property_value_buffer)

            # Entity Identifier
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
                "property_value": {"name": "Property Value"},
                "_memberorder": ["trig", "identifier", "property_name", "property_value"],
            }

            @modifier
            def set_property_value(self):
                self.set_property(self.identifier_buffer, self.property_name_buffer, self.property_value_buffer)

            trigger(trig, set_property_value)

            def set_set_property(self, set_property):
                self.set_property = set_property

            def set_get_entity(self, get_entity):
                self.get_entity = get_entity

            def place(self):
                if idmode == "bound":
                    libcontext.socket("entity", socket_single_required(self.set_get_entity))

                libcontext.socket(("entity", "set_property"), socket_single_required(self.set_set_property))

        return set_property
