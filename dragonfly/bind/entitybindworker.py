import bee
import libcontext

from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class entitybindworker(bee.worker):

    """Interfaces with binder drone"""

    v_hivemap = variable("id")
    startvalue(v_hivemap, "")

    v_entity_name = variable("id")
    startvalue(v_entity_name, "")

    entity_name_ = antenna("push", "id")
    connect(entity_name_, v_entity_name)

    hivemap_name = output("pull", "id")
    entity_name = output("pull", "id")

    trig = output("push", "trigger")

    connect(v_hivemap, hivemap_name)
    connect(v_entity_name, entity_name)

    trig_func = triggerfunc(trig)

    @modifier
    def pushed_bind(self):
        self.do_bind(self.entity_name_)

    trigger(v_entity_name, pushed_bind)

    def on_start(self):
        for entity_name in self.get_entity_names():
            self.do_bind(entity_name)

    def do_bind(self, entity_name):
        hivemap_name = self.get_hivemap_name(entity_name)
        if hivemap_name is None:
            return

        self.v_hivemap = hivemap_name
        self.v_entity_name = entity_name
        self.trig_func()

    def set_get_entity_names(self, plugin):
        self.get_entity_names = plugin

    def set_get_hivemap_name(self, plugin):
        self.get_hivemap_name = plugin

    def place(self):
        listener = plugin_single_required(("trigger", self.on_start, "start"))
        libcontext.plugin(("evin", "listener"), listener)

        plugin = plugin_supplier(self.do_bind)
        libcontext.plugin(("entity", "launch_registered_hivemap"), plugin)

        socket = socket_single_required(self.set_get_hivemap_name)
        libcontext.socket(("entity", "get_registered_hivemap_name"), socket)

        socket = socket_single_required(self.set_get_entity_names)
        libcontext.socket("get_entity_names", socket)
