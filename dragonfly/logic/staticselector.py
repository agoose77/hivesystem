import bee
from bee.segments import *


class staticselector(bee.worker):
    # selection pointer
    v_sel = variable("int")
    startvalue(v_sel, 0)

    #get selected identifier
    selected = output("pull", "id")
    v_selected = variable("id")
    connect(v_selected, selected)

    @modifier
    def get_selected(self):
        self.v_selected = self.identifiers[self.v_sel]

    pretrigger(v_selected, get_selected)

    #select last (v_sel = -1)
    last = variable("int")
    startvalue(last, -1)
    select_last = transistor("int")
    connect(last, select_last)
    connect(select_last, v_sel)

    #select by integer
    select = antenna("push", "int")
    connect(select, v_sel)

    #select by identifier
    select_identifier = antenna("push", "id")
    v_select_identifier = variable("id")
    connect(select_identifier, v_select_identifier)

    @modifier
    def m_select(self):
        self.v_sel = self.identifiers.index(self.v_select_identifier)

    trigger(v_select_identifier, m_select)

    #select next/prev
    select_next = antenna("push", "trigger")

    @modifier
    def m_select_next(self):
        sel = self.v_sel
        if sel < -1:
            sel = len(self.identifiers) - sel
            if sel < -1: sel = -1
        self.v_sel = sel + 1
        if self.v_sel == len(self.identifiers): self.v_sel = 0

    trigger(select_next, m_select_next)

    select_prev = antenna("push", "trigger")

    @modifier
    def m_select_prev(self):
        sel = self.v_sel
        if sel < -1:
            sel = len(self.identifiers) - sel
            if sel < -1: sel = -1
        if sel == -1: sel = len(self.identifiers)
        self.v_sel = sel - 1

    trigger(select_prev, m_select_prev)

    def register_identifier(self, identifier):
        ## This is called before instantiation (at Configure time), so we are dealing
        # with a wrapped object: self.bee
        try:
            self.bee.identifiers.append(identifier)
        except AttributeError:
            self.bee.identifiers = [identifier]
