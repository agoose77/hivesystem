# dragonfly.logic.containfilter

import bee
from bee.segments import *


class containfilter(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        class containfilter(bee.worker):
            unfiltered = antenna("push", type)
            v_unfiltered = variable(type)
            connect(unfiltered, v_unfiltered)

            container = antenna("pull", "object")
            b_container = buffer("pull", "object")
            connect(container, b_container)
            get_container = triggerfunc(b_container)

            filtered = output("push", type)
            b_filtered = buffer("push", type)
            connect(b_filtered, filtered)
            trig_filtered = triggerfunc(b_filtered)

            @modifier
            def do_filter(self):
                self.get_container()
                if self.v_unfiltered in self.b_container:
                    self.b_filtered = self.v_unfiltered
                    self.trig_filtered()

            trigger(v_unfiltered, do_filter)

        return containfilter

  
