import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *


class show2(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        inptype = (type, "id")

        class show2(bee.worker):
            inp = antenna("push", inptype)
            v_inp = variable(inptype)
            connect(inp, v_inp)

            @modifier
            def m_show(self):
                obj, identifier = self.v_inp
                self.show(obj, identifier)

            trigger(v_inp, m_show)

            def set_show(self, showfunc):
                self.show = showfunc

            def place(self):
                s = socket_single_required(self.set_show)
                libcontext.socket(("canvas", "show2", type), s)

        return show2

