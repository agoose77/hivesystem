import libcontext
from bee.bind import *


class stopforwarder(binderdrone):
    def stopfunc(self, bindname):
        self.binderworker.v_stop = bindname
        self.binderworker.m_stop()

    def bind(self, binderworker, bindname):
        self.binderworker = binderworker
        p = libcontext.pluginclasses.plugin_supplier(lambda: self.stopfunc(bindname))
        libcontext.plugin("stop", p)


class processbinder(binderdrone):

    def set_register_process(self, register_process):
        self.register_process = register_process

    def bind(self, binderworker, bindname):
        # Get stop for bound process
        p = libcontext.socketclasses.socket_single_required(lambda function: self.register_process(bindname, function))
        libcontext.socket("stop", p)

    def place(self):
        libcontext.socket(("process", "register"), libcontext.socketclasses.socket_single_required(self.set_register_process))


class bind(bind_baseclass):
    bind_exit = bindparameter(True)
    binder("bind_exit", False, None)
    binder("bind_exit", True, pluginbridge("exit"))
    binder("bind_exit", "stop", stopforwarder(), "bindname")

    bind_stop = bindparameter(True)
    binder("bind_stop", False, None)
    binder("bind_stop", True, stopforwarder(), "bindname")

    register_process = bindparameter(True)
    binder("register_process", False, None)
    binder("register_process", True, processbinder(), "bindname")