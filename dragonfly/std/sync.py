import bee
from bee.segments import *
import libcontext
from libcontext.pluginclasses import *


class sync(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        class sync(bee.worker):
            inp = antenna("pull", type)
            val = buffer("pull", type)
            connect(inp, val)
            get_inp = triggerfunc(val)

            outp = output("push", type)
            t = transistor(type)
            connect(val, t)
            connect(t, outp)
            trig = triggerfunc(t)

            def watch(self):
                old_val = self.val
                self.get_inp()
                if self.val != old_val: self.trig()

            def place(self):
                p = plugin_single_required(("trigger", self.watch, "tick"))
                libcontext.plugin(("evin", "listener"), p)

        return sync
      
  

