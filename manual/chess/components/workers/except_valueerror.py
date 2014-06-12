from __future__ import print_function

import bee, libcontext
from bee.segments import *
from libcontext.socketclasses import *


class except_valueerror(bee.worker):
    raisin = antenna("push", "exception")
    v_inp = variable("exception")
    connect(raisin, v_inp)

    @modifier
    def raising(self):
        if not self.raiser_active(): return
        if self.v_inp[1][0] == ValueError:
            print("Invalid move:", self.v_inp[1][1])
            self.v_inp.cleared = True

    trigger(v_inp, raising)

    def set_raiser_active(self, raiser_active):
        self.raiser_active = raiser_active

    def place(self):
        s = socket_single_required(self.set_raiser_active)
        libcontext.socket(("eventhandler", "raiser", "active"), s)
  
