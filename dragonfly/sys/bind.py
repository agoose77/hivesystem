import libcontext
from bee.bind import *

from libcontext.pluginclasses import *
from libcontext.socketclasses import *


class stopforwarder(binderdrone):

    def stopfunc(self, bindname):
        self.binderworker.v_stop = bindname
        self.binderworker.m_stop()

    def bind(self, binderworker, bindname):
        self.binderworker = binderworker
        p = plugin_supplier(lambda: self.stopfunc(bindname))
        libcontext.plugin("stop", p)


class processbinder(binderdrone):

    def set_register_stop_process(self, register_stop_process):
        self.register_stop_process = register_stop_process

    def set_register_suspend_process(self, register_suspend_process):
        self.register_suspend_process = register_suspend_process

    def set_register_resume_process(self, register_resume_process):
        self.register_resume_process = register_resume_process

    def set_unregister_process(self, unregister_process):
        self.unregister_process = unregister_process

    def set_suspend_process(self, suspend_process):
        self.suspend_process = suspend_process

    def set_resume_process(self, resume_process):
        self.resume_process = resume_process

    def set_stop_process(self, stop_process):
        self.stop_process = stop_process

    def set_get_hive(self, get_hive):
        self.get_hive = get_hive

    def set_register_hive(self, register_hive):
        self.register_hive = register_hive

    def set_launch_process(self, launch_process):
        self.launch_process  = launch_process

    def bind(self, binderworker, bindname):
        self.binderworker = binderworker

        # Local stop, suspend and resume functions (used by processmanager drone)
        def suspend_process():
            binderworker.v_pause = bindname
            binderworker.m_pause()

        def resume_process():
            binderworker.v_resume = bindname
            binderworker.m_resume()

        def stop_process():
            binderworker.v_stop = bindname
            binderworker.m_stop()

        # Register bound functions to process manager
        self.register_resume_process(bindname, resume_process)
        self.register_suspend_process(bindname, suspend_process)
        self.register_stop_process(bindname, stop_process)

        # When this process is cleaned up, unregister from the registered processes
        libcontext.plugin("cleanupfunction",
                          plugin_single_required(lambda: self.unregister_process(bindname)))

        # Give bound class global plugins if they need to use them
        libcontext.plugin(("process", "suspend"), plugin_supplier(self.suspend_process))
        libcontext.plugin(("process", "resume"), plugin_supplier(self.resume_process))
        libcontext.plugin(("process", "stop"), plugin_supplier(self.stop_process))
        libcontext.plugin(("process", "unregister"), plugin_supplier(self.unregister_process))
        libcontext.plugin(("process", "launch"), plugin_supplier(self.launch_process))

        # Setup functions
        libcontext.plugin(("process", "register", "suspend"), plugin_supplier(self.register_suspend_process))
        libcontext.plugin(("process", "register", "stop"), plugin_supplier(self.register_stop_process))
        libcontext.plugin(("process", "register", "resume"), plugin_supplier(self.register_resume_process))

        # Get current process ID
        libcontext.plugin(("process", "bound"), plugin_supplier(lambda: bindname))

        libcontext.plugin("register_hive", plugin_supplier(self.register_hive))
        libcontext.plugin("get_hive", plugin_supplier(self.get_hive))

    def place(self):
        libcontext.socket(("process", "register", "stop"),
                          socket_single_required(self.set_register_stop_process))
        libcontext.socket(("process", "register", "suspend"),
                          socket_single_required(self.set_register_suspend_process))
        libcontext.socket(("process", "register", "resume"),
                          socket_single_required(self.set_register_resume_process))
        libcontext.socket(("process", "unregister"),
                          socket_single_required(self.set_unregister_process))

        # There is no point in binding locally the suspend/resume functions
        # As they are intended to be reversible, yet this hive would not be able to resume when suspendd
        libcontext.socket(("process", "suspend"),
                          socket_single_required(self.set_suspend_process))
        libcontext.socket(("process", "resume"),
                          socket_single_required(self.set_resume_process))
        libcontext.socket(("process", "stop"),
                          socket_single_required(self.set_stop_process))
        libcontext.socket(("process", "launch"),
                          socket_single_required(self.set_launch_process))

        libcontext.socket("get_hive",
                          socket_single_required(self.set_get_hive))
        libcontext.socket("register_hive",
                          socket_single_required(self.set_register_hive))


class bind(bind_baseclass):
    bind_exit = bindparameter(True)
    binder("bind_exit", False, None)
    binder("bind_exit", True, pluginbridge("exit"))

    bind_stop = bindparameter(True)
    binder("bind_stop", False, None)
    binder("bind_stop", True, stopforwarder(), "bindname")

    bind_process = bindparameter(True)
    binder("bind_process", False, None)
    binder("bind_process", True, processbinder(), "bindname")