import bee
import libcontext
import Spyder
from bee.spyderhive.hivemaphive import hivemapinithive

from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class startupentitybinderdrone(bee.drone):

    """Provides plugins for scene-object binding on startup"""

    def on_start(self):
        """When the game starts, iterate over entities and launch processes"""
        for entity_name in self.get_entity_names():
            try:
                hivemap_name = self.get_property(entity_name, "hivemap")

            except KeyError:
                continue

            self.launch_hive(hivemap_name, entity_name)

    def set_get_property(self, plugin):
        self.get_property = plugin

    def set_get_entity_names(self, plugin):
        self.get_entity_names = plugin

    def set_launch_hive(self, launch_hive):
        self.launch_hive = launch_hive

    def place(self):
        socket = socket_single_required(self.set_get_entity_names)
        libcontext.socket("get_entity_names", socket)

        listener = plugin_single_required(("trigger", self.on_start, "start"))
        libcontext.plugin(("evin", "listener"), listener)

        socket = socket_single_required(self.set_get_property)
        libcontext.socket(("entity", "property", "get"), socket)

        socket = socket_single_required(self.set_launch_hive)
        libcontext.socket(("process", "launch"), socket)