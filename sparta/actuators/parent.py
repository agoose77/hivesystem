import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class parent(object):
    """
    The parent actuator re-parents one 3D object to another
    In bound mode, the 3D object that is re-parented is the one that is bound to the hive
    """
    metaguiparams = {
        "idmode": "str",
        "autocreate": {"idmode": "unbound"},
    }

    @classmethod
    def form(cls, f):
        f.idmode.name = "ID mode"
        f.idmode.advanced = True
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound"
        f.idmode.default = "unbound"
        f.idmode.optiontitles = "Unbound", "Bound"

    def __new__(cls, idmode):
        assert idmode in ("bound", "unbound"), idmode

        class parent(bee.worker):
            __doc__ = cls.__doc__

            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))
                identifier_buffer = buffer("pull", ("str", "identifier"))
                connect(identifier, identifier_buffer)


            trig = antenna("push", "trigger")
            parent = antenna("pull", ("str", "identifier"))
            parent_buffer = buffer("pull", ("str", "identifier"))
            connect(parent, parent_buffer)
            trigger(trig, parent_buffer)

            guiparams = {
                "trig": {"name": "Trigger"},
                "identifier": {"name": "Identifier", "fold": True},
                "parent": {"name": "Parent"},
                "_memberorder": ["trig", "identifier", "parent"],
            }

            if idmode == "bound":
                @modifier
                def m_parent(self):
                    self.parent_func(self.entity.entityname, self.parent_buffer)

                def set_entity(self, entity):
                    self.entity = entity

            elif idmode == "unbound":
                @modifier
                def m_parent(self):
                    self.parent_func(self.identifier_buffer, self.parent_buffer)

                trigger(trig, identifier_buffer)

            trigger(trig, m_parent)

            def set_entity_parent_to(self, parent_func):
                self.parent_func = parent_func

            def place(self):
                if idmode == "bound":
                    libcontext.socket("entity", socket_single_required(self.set_entity))

                socket_info = libcontext.socketclasses.socket_single_required(self.set_entity_parent_to)
                libcontext.socket(("entity", "parent_to"), socket_info)

        return parent
