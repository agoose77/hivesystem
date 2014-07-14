import bee
import libcontext

from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

import Spyder
from bee.spyderhive.hivemaphive import hivemapinithive


class bindworkerinterface(bee.worker):
    """Interfaces with binder drone and a bindworker.

    Exposes hivemap name, bind name and trigger outputs to drive a bind worker
    """

    v_hivemap = variable("id")
    startvalue(v_hivemap, "")

    v_process_class = variable("id")
    startvalue(v_process_class, "")

    hivemap_name = output("pull", "id")
    process_identifier = output("pull", "id")

    trig = output("push", "trigger")
    trig_func = triggerfunc(trig)

    connect(v_hivemap, hivemap_name)
    connect(v_process_class, process_identifier)

    def do_bind(self, process_class_identifier, process_identifier):
        """Trigger bindworker with hivemap name and process identifier

        :param process_class_identifier: identifier of process class
        :param process_identifier: identifier of process to launch
        """

        self.v_hivemap = process_class_identifier
        self.v_process_class = process_identifier

        # Trigger bindworker
        self.trig_func()

    def set_register_hive(self, register_func):
        self.register_func = register_func

    def set_get_hive(self, get_func):
        self.get_func = get_func

    def place(self):
        plugin = plugin_supplier(self.do_bind)
        libcontext.plugin(("process", "launch"), plugin)

        socket = socket_single_required(self.set_register_hive)
        libcontext.socket("register_hive", socket)

        socket = socket_single_required(self.set_get_hive)
        libcontext.socket("get_hive", socket)
