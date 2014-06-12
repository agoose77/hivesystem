import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class action3_play_sound(bee.worker):
    def set_playfunc(self, playfunc):
        self.play = playfunc

    @modifier
    def do_play(self):
        self.play(self.v_inp)

    inp = antenna('push', 'id')

    v_inp = variable('id')

    trigger(v_inp, do_play)
    connect(inp, v_inp)

    def place(self):
        s = socket_single_required(self.set_playfunc)
        libcontext.socket(("sound", "play"), s)
    
    
    
