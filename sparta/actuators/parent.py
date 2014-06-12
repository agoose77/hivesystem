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

            trig = antenna("push", "trigger")
            parent = antenna("pull", ("str", "identifier"))

            guiparams = {
                "trig": {"name": "Trigger"},
                "identifier": {"name": "Identifier", "fold": True},
                "parent": {"name": "Parent"},
                "_memberorder": ["trig", "identifier", "parent"],
            }

            def place(self):
                raise NotImplementedError("sparta.actuators.parent has not been implemented yet")

        return parent
    