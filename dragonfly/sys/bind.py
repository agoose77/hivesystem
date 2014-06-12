import libcontext
from bee.bind import *


class stopforwarder(binderdrone):
    def stopfunc(self):
        self.binderworker.v_stop = self.bindname
        self.binderworker.m_stop()

    def bind(self, binderworker, bindname):
        self.binderworker = binderworker
        self.bindname = bindname
        p = libcontext.pluginclasses.plugin_supplier(self.stopfunc)
        libcontext.plugin("stop", p)


class bind(bind_baseclass):
    bind_exit = bindparameter(True)
    binder("bind_exit", False, None)
    binder("bind_exit", True, pluginbridge("exit"))
    binder("bind_exit", "stop", stopforwarder(), "bindname")
    bind_stop = bindparameter(True)
    binder("bind_stop", False, None)
    binder("bind_stop", True, stopforwarder(), "bindname")
