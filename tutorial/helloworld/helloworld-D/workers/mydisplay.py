import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class mydisplay(object):
    metaguiparams = {"vartype": "type"}

    def __new__(cls, vartype):
        class mydisplay(bee.worker):
            def set_displayfunc(self, displayfunc):
                self.display = displayfunc

            @modifier
            def do_display(self):
                self.display(self.v_string)


            string = antenna('push', vartype)

            v_string = variable(vartype)

            connect(string, v_string)
            trigger(v_string, do_display)

            def place(self):
                s = socket_single_required(self.set_displayfunc)
                libcontext.socket("display", s)

        return mydisplay