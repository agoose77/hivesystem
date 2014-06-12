import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *


class draw2(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        inptype = (type, ("object", "box2d"), "id")

        class draw2(bee.worker):
            inp = antenna("push", inptype)
            v_inp = variable(inptype)
            connect(inp, v_inp)

            @modifier
            def m_draw(self):
                obj, bbox, identifier = self.v_inp
                self.draw(obj, bbox, identifier)

            trigger(v_inp, m_draw)

            def set_draw(self, drawfunc):
                self.draw = drawfunc

            def place(self):
                s = socket_single_required(self.set_draw)
                libcontext.socket(("canvas", "draw2", type), s)

        return draw2

