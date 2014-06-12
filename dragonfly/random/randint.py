from __future__ import absolute_import

import bee
from bee.segments import *
import random as random_module


class randint(bee.worker):
    minmax = antenna("pull", ("int", "int"))
    b_minmax = buffer("pull", ("int", "int"))
    connect(minmax, b_minmax)
    get_minmax = triggerfunc(b_minmax, "update")

    outp = output("pull", "int")
    v_outp = variable("int")
    connect(v_outp, outp)

    @modifier
    def m_randint(self):
        self.get_minmax()
        vmin, vmax = self.b_minmax
        self.v_outp = random_module.randint(vmin, vmax)

    pretrigger(v_outp, m_randint)
