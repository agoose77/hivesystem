import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class stop(bee.worker):
    """Stops the current hive. If "delobj" is True, delete any object bound to the hive.
    In case of the top-level hive, this quits the game.
    """
    # Inputs and outputs
    trig = antenna("push", "trigger")

    delobj = variable("bool")
    # TODO fix defaults from sticking
    parameter(delobj)

    @classmethod
    def form(self, f):
        f.delobj.name = "Delete object"

    # Define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
    }

    @modifier
    def do_stop(self):
        if self.delobj and hasattr(self, "remove_entity"):
            self.remove_entity()

        else:
            self.stop_func()

    trigger(trig, do_stop)

    def set_stop_func(self, stop_func):
        self.stop_func = stop_func

    def set_entity(self, entity_name):
        self.entity_name = entity_name()

    def set_remove_entity(self, remove_entity):
        self.remove_entity = remove_entity

    def place(self):
        libcontext.socket(("entity", "bound", "remove"), socket_single_optional(self.set_remove_entity))
        libcontext.socket(("entity", "bound"), socket_single_optional(self.set_entity))

        libcontext.socket("stop", socket_single_required(self.set_stop_func))
