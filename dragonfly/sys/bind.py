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

    def set_register_stop_process(self, register_stop_process):
        self.register_stop_process = register_stop_process

    def set_register_pause_process(self, register_pause_process):
        self.register_pause_process = register_pause_process

    def set_register_resume_process(self, register_resume_process):
        self.register_resume_process = register_resume_process

    def set_unregister_process(self, unregister_process):
        self.unregister_process = unregister_process

    def set_pause_process(self, pause_process):
        self.pause_process = pause_process

    def set_resume_process(self, resume_process):
        self.resume_process = resume_process

    def do_stop_process(self, bind_name):
        self.binderworker.v_stop = bind_name
        self.binderworker.m_stop()

    def do_pause_process(self, bind_name):
        self.binderworker.v_pause = bind_name
        self.binderworker.m_pause()

    def do_resume_process(self, bind_name):
        self.binderworker.v_resume = bind_name
        self.binderworker.m_resume()

    def bind(self, binderworker, bindname):
        self.binderworker = binderworker

        # Local bound functions
        def stop():
            self.do_stop_process(bindname)

        def pause():
            self.do_pause_process(bindname)

        def resume():
            self.do_resume_process(bindname)

        # Register bound functions to process controller
        self.register_stop_process(bindname, stop)
        self.register_resume_process(bindname, resume)
        self.register_pause_process(bindname, pause)

        # When this process is cleaned up, unregister from the registered processes
        libcontext.plugin("cleanupfunction",
                          libcontext.pluginclasses.plugin_single_required(lambda: self.unregister_process(bindname)))
        # Give bound class pause global plugin
        libcontext.plugin(("process", "pause"), libcontext.pluginclasses.plugin_supplier(self.pause_process))
        libcontext.plugin(("process", "resume"), libcontext.pluginclasses.plugin_supplier(self.resume_process))

    def place(self):
        libcontext.socket(("process", "register", "stop"),
                          libcontext.socketclasses.socket_single_required(self.set_register_stop_process))
        libcontext.socket(("process", "register", "pause"),
                          libcontext.socketclasses.socket_single_required(self.set_register_pause_process))
        libcontext.socket(("process", "register", "resume"),
                          libcontext.socketclasses.socket_single_required(self.set_register_resume_process))
        libcontext.socket(("process", "unregister"),
                          libcontext.socketclasses.socket_single_required(self.set_unregister_process))

        libcontext.socket(("process", "pause"),
                          libcontext.socketclasses.socket_single_required(self.set_pause_process))
        libcontext.socket(("process", "resume"),
                          libcontext.socketclasses.socket_single_required(self.set_resume_process))


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