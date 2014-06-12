import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class game_object(object):
    """
The Game Object assessor returns a Blender Game Engine game object (KX_GameObject)
    """
    metaguiparams = {
        "idmode": "str",
        "autocreate": {"idmode": "bound"},
    }

    @classmethod
    def form(cls, f):
        f.idmode.name = "ID mode"
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound"
        f.idmode.default = "bound"
        f.idmode.optiontitles = "Unbound", "Bound"

    def __new__(cls, idmode):
        assert idmode in ("bound", "unbound"), idmode

        class game_object(bee.worker):
            __doc__ = cls.__doc__
            obj = output("pull", ("object", "bge"))
            b_obj = buffer("pull", ("object", "bge"))
            connect(b_obj, obj)

            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))

            # Name the inputs and outputs
            guiparams = {
                "identifier": {"name": "Identifier"},
                "obj": {"name": "Object"},
            }

            def place(self):
                raise NotImplementedError("sparta.assessors.game_object has not been implemented yet")

        return game_object
