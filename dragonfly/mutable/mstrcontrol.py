import bee
from bee.segments import *


class mstrcontrol(bee.worker):
    mstr = antenna("pull", "mstr")
    b_mstr = buffer("pull", "mstr")
    connect(mstr, b_mstr)

    value = output("pull", "str")
    b_value = buffer("pull", "str")
    connect(b_value, value)

    @modifier
    def m_get_value(self):
        self.b_value = self.b_mstr.value
        if self.b_value is None: self.b_value = ""

    pretrigger(b_value, b_mstr, "output")
    pretrigger(b_value, m_get_value, "output")

    set = antenna("push", "str")
    v_set = variable("str")
    connect(set, v_set)

    @modifier
    def m_set(self):
        self.b_mstr.value = self.v_set

    trigger(v_set, b_mstr)
    trigger(v_set, m_set)
  
