import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from ..drone import drone
from .pinworker import pinworker
from .. import hivesubclass, hiveinstance, _hivesubclass


class create(drone):
    def __call__(self, w, contextname):
        if not hiveinstance(w, pinworker):
            raise TypeError("Cannot create new pinworker: first argument is not a pinworker")
        try:
            libcontext.push(self.contextname)
            ww = w.getinstance()
            ww.build(contextname)
            ww.parent = self.parent
            ww.place()
            ww.close()
        finally:
            libcontext.pop()
        return ww

    def set_parent(self, parent):
        self.parent = parent

    def place(self):
        self.contextname = libcontext.get_curr_contextname()
