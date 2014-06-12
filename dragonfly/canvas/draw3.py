import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *


def err(typ1, typ2):
    return TypeError("""
Object type for reserved identifier does not match draw3 meta-parameter:
%s vs %s
""" % (typ1, typ2)
    )


class draw3(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        class draw3(bee.worker):
            identifier = variable("id")
            parameter(identifier)

            static = variable("bool")
            parameter(static, True)

            inp = antenna("push", type)
            v_inp = variable(type)
            connect(inp, v_inp)

            @modifier
            def m_draw(self):
                if self.static:
                    reserve = self.reserve
                    type_, bbox, parameters = reserve
                    self.draw(self.v_inp, bbox, self.identifier, parameters=parameters)
                else:
                    self.draw(self.v_inp, self.identifier)

            trigger(v_inp, m_draw)

            def set_draw(self, drawfunc):
                self.draw = drawfunc

            def set_reserve(self, type_, bbox, parameters):
                if type_ is not None and type_ != type:
                    raise err(type_, type)
                self.reserve = type_, bbox, parameters

            def place(self):
                if self.static:
                    s = socket_single_required(self.set_draw)
                    libcontext.socket(("canvas", "draw2", type), s)
                    s = socket_single_required(self.set_reserve)
                    libcontext.socket(("canvas", "reserve", self.identifier), s)
                else:
                    s = socket_single_required(self.set_draw)
                    libcontext.socket(("canvas", "draw3", type), s)

        return draw3

