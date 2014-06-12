import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *


class show1(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        class show1(bee.worker):
            inp = antenna("push", type)
            v_inp = variable(type)
            connect(inp, v_inp)

            @modifier
            def m_show(self):
                identifier = self.show(self.v_inp)
                self.v_id = identifier

            trigger(v_inp, m_show)
            identifier = output("pull", "id")
            v_id = buffer("pull", "id")
            connect(v_id, identifier)

            def set_show(self, showfunc):
                self.show = showfunc

            def place(self):
                s = socket_single_required(self.set_show)
                libcontext.socket(("canvas", "show1", type), s)

        return show1

