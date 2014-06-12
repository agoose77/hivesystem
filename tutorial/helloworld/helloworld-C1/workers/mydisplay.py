import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class mydisplay(bee.worker):
    @modifier
    def do_display(self):
        print(self.v_string)

    string = antenna('push', 'str')

    v_string = variable('str')

    connect(string, v_string)
    trigger(v_string, do_display)