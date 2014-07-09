import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class stop(object):

    metaguiparams = {
        "idmode": "str",
        "autocreate": {"idmode": "bound"},
    }


    @classmethod
    def form(cls, f):
        f.idmode.name = "ID mode"
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound", "fallback"
        f.idmode.optiontitles = "Unbound", "Bound", "Fallback"
        f.idmode.default = "bound"

    def __new__(cls, idmode):
        assert idmode in ("bound", "unbound", "fallback"), idmode

        class stop(bee.worker):
            """Stops the current hive. If "delobj" is True, delete any object bound to the hive.
            In case of the top-level hive, this quits the game.
            """
            # Inputs and outputs
            trig = antenna("push", "trigger")
            delobj = variable("bool")
            # TODO fix defaults from sticking
            parameter(delobj)

            # Define the I/O names
            guiparams = {
                "trig": {"name": "Trigger"},
            }

            @modifier
            def do_stop(self):
                if idmode == "bound" and self.delobj:
                    self.remove_entity()

                else:
                    self.stop_func()

            trigger(trig, do_stop)

            @classmethod
            def form(self, f):
                f.delobj.name = "Delete object"

            def set_stop_func(self, stop_func):
                self.stop_func = stop_func

            if idmode == "bound":
                def set_entity(self, entity_name):
                    self.entity_name = entity_name()

                def set_remove_entity(self, remove_entity):
                    self.remove_entity = remove_entity

            def place(self):
                if idmode == "bound":
                    libcontext.socket(("entity", "bound", "remove"), socket_single_required(self.set_remove_entity))
                    libcontext.socket(("entity", "bound"), socket_single_required(self.set_entity))
                libcontext.socket("stop", socket_single_required(self.set_stop_func))

        return stop