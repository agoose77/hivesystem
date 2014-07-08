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
                    self.parent_set(self.parent_buffer)

                def set_parent_set(self, parent_set):
                    self.parent_set = parent_set


            elif idmode == "unbound":
                @modifier
                def m_parent(self):
                    self.parent_set_for(self.identifier_buffer, self.parent_buffer)

                def set_parent_set_for(self, parent_set_for):
                    self.parent_set_for = parent_set_for

                trigger(trig, identifier_buffer)

            trigger(trig, m_parent)

            def place(self):
                if idmode == "bound":
                    libcontext.socket(("entity", "bound", "parent", "set"),
                                      socket_single_required(self.set_parent_set))

                else:
                    libcontext.socket(("entity", "parent", "set"), socket_single_required(self.set_parent_set_for))

        return parent
