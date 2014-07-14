import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class view(object):

    """The view assessor returns a view matrix, that can be manipulated to re-position an object in 3D space"""

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
            view = output("pull", ("object", "matrix"))
            b_view = buffer("pull", ("object", "matrix"))
            connect(b_view, view)
            viewmode = variable("str")
            parameter(viewmode)

            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))

            # Name the inputs and outputs
            guiparams = {
                "identifier": {"name": "Identifier"},
                "view": {"name": "View"},
            }

            @classmethod
            def form(cls, f):
                f.viewmode.name = "View mode"
                f.viewmode.options = "world", "parent", "local", "relative", "offset"
                f.viewmode.optiontitles = "World view", "Parent view", "Local view", "Relative view", "Offset view"
                f.viewmode.advanced_options = "relative", "offset"
                f.viewmode.default = "parent"

            def place(self):
                raise NotImplementedError("sparta.assessors.view has not been implemented yet")

        return view
