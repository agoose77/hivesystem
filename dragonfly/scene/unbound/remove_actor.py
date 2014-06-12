import bee
from bee.segments import *
import libcontext


class remove_actor(bee.worker):
    inp = antenna("push", "id")
    v_inp = variable("id")
    connect(inp, v_inp)

    @modifier
    def m_remove(self):
        self.remove_actor(self.v_inp)

    trigger(v_inp, m_remove)

    def set_remove_actor(self, remove_actor):
        self.remove_actor = remove_actor

    def place(self):
        s = libcontext.socketclasses.socket_single_required(self.set_remove_actor)
        libcontext.socket(("remove", "actor"), s)
