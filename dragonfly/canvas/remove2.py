import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *


class remove2(bee.worker):
    identifier = antenna("push", "id")
    v_id = variable("id")
    connect(identifier, v_id)

    @modifier
    def do_remove(self):
        for remover in self.removers:
            processed = remover(self.v_id)
            if processed: break

    trigger(v_id, do_remove)

    def add_remover(self, remover):
        self.removers.append(remover)

    def place(self):
        self.removers = []
        s = socket_container(self.add_remover)
        libcontext.socket(("canvas", "remove1"), s)
