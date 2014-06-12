import bee
from bee.segments import *


class selector(bee.worker):
    # selection pointer
    v_sel = variable("int")
    startvalue(v_sel, 0)

    #flag: list of identifiers is empty?
    empty = output("pull", "bool")
    v_empty = variable("bool")
    startvalue(v_empty, True)
    connect(v_empty, empty)

    #get selected identifier
    selected = output("pull", "id")
    v_selected = variable("id")
    connect(v_selected, selected)

    @modifier
    def get_selected(self):
        self.v_selected = self.identifiers[self.v_sel]

    pretrigger(v_selected, get_selected)

    #register a new identifier
    register = antenna("push", "id")
    v_register = variable("id")
    connect(register, v_register)

    @modifier
    def register_identifier(self):
        if self.v_register in self.identifiers: raise KeyError(self.v_register)
        self.identifiers.append(self.v_register)
        self.v_empty = False

    trigger(v_register, register_identifier)

    #select last (v_sel = -1)
    last = variable("int")
    startvalue(last, -1)
    select_last = transistor("int")
    connect(last, select_last)
    connect(select_last, v_sel)

    #register and select last
    register_and_select = antenna("push", "id")
    b_register_and_select = buffer("push", "id")
    connect(register_and_select, b_register_and_select)
    connect(b_register_and_select, v_register)
    trigger(b_register_and_select, b_register_and_select, "input")
    trigger(b_register_and_select, select_last)

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


    #unregister selected

    unregister = antenna("push", "trigger")

    @modifier
    def m_unregister(self):
        self.identifiers.pop(self.v_sel)
        if not self.identifiers: self.v_empty = True
        if self.v_sel >= len(self.identifiers): self.v_sel = -1

    trigger(unregister, m_unregister)

    #unregister by identifier
    unregister_identifier = antenna("push", "id")
    v_unregister = variable("id")
    connect(unregister_identifier, v_unregister)

    @modifier
    def m_unregister_identifier(self):
        self.identifiers.remove(self.v_unregister)
        if not self.identifiers: self.v_empty = True
        if self.v_sel >= len(self.identifiers): self.v_sel = -1

    trigger(v_unregister, m_unregister_identifier)

    def place(self):
        self.identifiers = []
    
