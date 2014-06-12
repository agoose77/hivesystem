import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class mydisplay(bee.worker):
    def set_displayfunc(self, displayfunc):
        self.display = displayfunc

    @modifier
    def do_display(self):
        self.display(self.v_string)


    string = antenna('push', 'str')

    v_string = variable('str')

    connect(string, v_string)
    trigger(v_string, do_display)

    def place(self):
        s = socket_single_required(self.set_displayfunc)
        libcontext.socket("display", s)