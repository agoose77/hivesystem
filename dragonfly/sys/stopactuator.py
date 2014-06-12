import bee, libcontext
from bee.segments import *


class stopactuator(bee.worker):
    inp = antenna("push", "trigger")

    @modifier
    def call_stopfunc(self):
        self.stopfunc()

    trigger(inp, call_stopfunc)

    def set_stopfunc(self, stopfunc):
        assert hasattr(stopfunc, "__call__")
        self.stopfunc = stopfunc

    def place(self):
        socketclass = libcontext.socketclasses.socket_single_required
        libcontext.socket("stop", socketclass(self.set_stopfunc))
  
