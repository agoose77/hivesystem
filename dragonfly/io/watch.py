import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class watch(object):
    metaguiparams = {"type_inp": "type"}

    def __new__(cls, type_inp):
        class watch(bee.worker):
            header = variable("str")
            parameter(header, "Value:")
            inp = antenna("pull", type_inp)

            v_inp = variable(type_inp)
            t_inp = transistor(type_inp)
            connect(inp, t_inp)
            connect(t_inp, v_inp)
            trigger_inp = triggerfunc(t_inp)

            def watch(self):
                self.trigger_inp()
                if self.v_inp != self.old_value:
                    self.watchfunc(self.header, self.v_inp)
                    self.old_value = self.v_inp

            def set_watch(self, watchfunc):
                self.watchfunc = watchfunc

            def place(self):
                self.old_value = None
                p = plugin_single_required(("trigger", self.watch, "tick"))
                libcontext.socket("watch", socket_single_required(self.set_watch))
                libcontext.plugin(("evin", "listener"), p)

        return watch
