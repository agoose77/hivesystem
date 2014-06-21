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
            obj_variable = variable(("object", "bge"))
            connect(obj_variable, obj)

            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))
                identifier_buffer = buffer("pull", ("str", "identifier"))
                connect(identifier, identifier_buffer)
                pretrigger(obj_variable, identifier_buffer)

            else:
                @property
                def identifier_buffer(self):
                    return self.get_entity().entityname

            @modifier
            def get_bge_obj(self):
                identifier = self.identifier_buffer
                self.obj_variable = self.lookup_entity(identifier)

            pretrigger(obj_variable, get_bge_obj)

            # Name the inputs and outputs
            guiparams = {
                "identifier": {"name": "Identifier"},
                "obj": {"name": "Object"},
            }

            def set_get_entity(self, get_entity):
                self.get_entity = get_entity

            def set_lookup_entity(self, get_entity):
                self.lookup_entity = get_entity

            def place(self):
                if idmode == "bound":
                    libcontext.socket("entity", socket_single_required(self.set_get_entity))

                libcontext.socket(("get_entity", "Blender"), socket_single_required(self.set_lookup_entity))


        return game_object
