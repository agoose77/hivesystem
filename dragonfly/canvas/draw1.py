import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *


class draw1(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        inptype = (type, ("object", "box2d"))

        class draw1(bee.worker):
            inp = antenna("push", inptype)
            v_inp = variable(inptype)
            connect(inp, v_inp)

            @modifier
            def m_draw(self):
                obj, bbox = self.v_inp
                identifier = self.draw(obj, bbox)
                self.v_id = identifier

            trigger(v_inp, m_draw)
            identifier = output("pull", "id")
            v_id = variable("id")
            connect(v_id, identifier)

            def set_draw(self, drawfunc):
                self.draw = drawfunc

            def place(self):
                s = socket_single_required(self.set_draw)
                libcontext.socket(("canvas", "draw1", type), s)

        return draw1

