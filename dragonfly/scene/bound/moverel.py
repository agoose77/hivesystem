from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


def get_worker(name, xyz):
    class moverel(worker):
        """Relative movement along %s axis""" % xyz
        __beename__ = name
        moverel = antenna("push", "float")
        movement = variable("float")
        connect(moverel, movement)

        @modifier
        def do_move(self):
            axis = self.get_matrix().get_proxy("AxisSystem")
            axis.origin += getattr(axis, xyz) * self.movement
            axis.commit()

        trigger(movement, do_move)

        def set_get_matrix(self, function):
            self.get_matrix = function

        def place(self):
            libcontext.socket(("entity", "bound", "matrix"), socket_single_required(self.set_get_matrix))

    return moverel


moverelX = get_worker("moverelX", "x")
moverelY = get_worker("moverelY", "y")
moverelZ = get_worker("moverelZ", "z")

