from __future__ import print_function
from itertools import chain

import bee

import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *


class processmanager(bee.drone):

    """Manages bound process instances"""

    def __init__(self):
        self._registered_stop_processes = {}
        self._registered_pause_processes = {}
        self._registered_resume_processes = {}

    def pause_process(self, process_name):
        try:
            pause_func = self._registered_pause_processes[process_name]
        except KeyError:
            return

        pause_func()

    def resume_process(self, process_name):
        try:
            resume_func = self._registered_resume_processes[process_name]
        except KeyError:
            return

        resume_func()

    def stop_process(self, process_name):
        try:
            stop_func = self._registered_stop_processes[process_name]
        except KeyError:
            return

        stop_func()

    def register_stop_process(self, process_name, stop_process):
        self._registered_stop_processes[process_name] = stop_process

    def register_resume_process(self, process_name, resume_process):
        self._registered_resume_processes[process_name] = resume_process

    def register_pause_process(self, process_name, pause_process):
        self._registered_pause_processes[process_name] = pause_process

    def unregister_process(self, process_name):
        """Unregister registered process from registration dictionaries.

        This should be called once the processes has been stopped, from the stop function.

        :param process_name: name of process to unregister
        """
        for process_dict in (self._registered_pause_processes, self._registered_stop_processes,
                             self._registered_resume_processes):
            if process_name in process_dict:
                process_dict.pop(process_name)

    def stop_all_processes(self):
        """Unregister all processes"""
        stop_processes = self._registered_stop_processes

        for process_name, stop_function in list(stop_processes.items()):
            stop_function()

    def place(self):
        libcontext.plugin(("process", "register", "stop"), plugin_supplier(self.register_stop_process))
        libcontext.plugin(("process", "register", "resume"), plugin_supplier(self.register_resume_process))
        libcontext.plugin(("process", "register", "pause"), plugin_supplier(self.register_pause_process))
        libcontext.plugin(("process", "unregister"), plugin_supplier(self.unregister_process))
        libcontext.plugin(("process", "pause"), plugin_supplier(self.pause_process))
        libcontext.plugin(("process", "resume"), plugin_supplier(self.resume_process))
        libcontext.plugin(("process", "stop"), plugin_supplier(self.stop_process))

        libcontext.plugin("cleanupfunction", plugin_single_required(self.stop_all_processes))
