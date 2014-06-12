import bee
import libcontext
from bee.segments import *


class hide(bee.worker):
    hide = antenna("push", "trigger")
    entity = antenna("pull", "id")
    b_entity = buffer("pull", "id")
    connect(entity, b_entity)
    trigger(hide, b_entity)

    @modifier
    def do_hide(self):
        self.hide(self.b_entity)

    trigger(hide, do_hide)

    def set_hide(self, hide):
        self.hide = hide

    def place(self):
        s = libcontext.socketclasses.socket_single_required(self.set_hide)
        libcontext.socket(("entity", "hide"), s)
    
