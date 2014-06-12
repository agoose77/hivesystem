import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *


class draw4(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        inptype = (type, ("object", "box2d"))

        class draw4(bee.worker):
            identifier = variable("id")
            parameter(identifier)

            inp = antenna("push", inptype)
            v_inp = variable(inptype)
            connect(inp, v_inp)

            @modifier
            def m_draw(self):
                obj, bbox = self.v_inp
                self.draw(obj, bbox, self.identifier)

            trigger(v_inp, m_draw)

            def set_draw(self, drawfunc):
                self.draw = drawfunc

            def place(self):
                s = socket_single_required(self.set_draw)
                libcontext.socket(("canvas", "draw2", type), s)

        return draw4

