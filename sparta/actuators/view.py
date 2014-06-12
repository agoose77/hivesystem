import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class view(object):
    """
    When triggered, the view actuator sets the other view matrix for the "relative" and "offset" view modes
    The view matrix is first converted to world coordinates; it is not automatically updated when the input matrix changes    
    """
    metaguiparams = {
        "idmode": "str",
        "autocreate": {"idmode": "bound"},
    }

    @classmethod
    def form(cls, f):
        f.idmode.name = "ID mode"
        f.idmode.advanced = True
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound"
        f.idmode.default = "bound"
        f.idmode.optiontitles = "Unbound", "Bound"

    def __new__(cls, idmode):
        assert idmode in ("bound", "unbound"), idmode

        class view(bee.worker):
            __doc__ = cls.__doc__

            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))

            mode = variable("str")
            parameter(mode)

            trig = antenna("push", "trigger")
            view = antenna("pull", ("object", "matrix"))

            @staticmethod
            def form(f):
                f.mode.name = "Mode"
                f.mode.type = "option"
                f.mode.default = "relative"
                f.mode.options = "relative", "offset"
                f.mode.optiontitles = "Relative", "Offset"

            guiparams = {
                "trig": {"name": "Trigger"},
                "identifier": {"name": "Identifier", "fold": True},
                "_memberorder": ["identifier", "trig"]
            }

            def place(self):
                raise NotImplementedError("sparta.actuators.view has not been implemented yet")

        return view
    