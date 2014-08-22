import bee
import libcontext
import Spyder
from bee.spyderhive.hivemaphive import hivemapinithive

from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class startup_binder_drone(bee.drone):

    """Provides plugins for scene-object binding on startup"""

    def on_start(self):
        """When the game starts, iterate over entities and launch processes"""
        for entity_name in self.get_entity_names():
            try:
                hivemap_name = self.get_hivemap(entity_name)

            except KeyError:
                continue

            # Check if it is registered
            self.check_hivemap_registered(hivemap_name)

            # Launch it
            self.launch_hive(hivemap_name, entity_name)

    def check_hivemap_registered(self, hivemap_name):
        try:
            self.get_hive(hivemap_name)

        # Else register it so the dragonfly.bind mixin can access it
        except KeyError:
            try:
                hivemap_ = Spyder.Hivemap.fromfile(hivemap_name)

            except Exception:
                print("Couldn't find hivemap {} to launch".format(hivemap_name))
                return

            wrapper_hive = type(hivemap_name, (hivemapinithive,), dict(hivemap=hivemap_))
            self.register_hive(hivemap_name, wrapper_hive)

    def set_get_hivemap(self, get_hivemap):
        self.get_hivemap = get_hivemap

    def set_get_entity_names(self, plugin):
        self.get_entity_names = plugin

    def set_launch_hive(self, launch_hive):
        self.launch_hive = launch_hive

    def set_register_hive(self, register_hive):
        self.register_hive = register_hive

    def set_get_hive(self, get_hive):
        self.get_hive = get_hive

    def place(self):
        socket = socket_single_required(self.set_get_entity_names)
        libcontext.socket(("entity", "names"), socket)

        listener = plugin_single_required(("trigger", self.on_start, "start", 9))
        libcontext.plugin(("evin", "listener"), listener)

        # Get hive name
        socket = socket_single_required(self.set_get_hivemap)
        libcontext.socket(("entity", "hivemap"), socket)

        socket = socket_single_required(self.set_launch_hive)
        libcontext.socket(("process", "launch"), socket)

        # We might need to register some hives on startup
        socket = socket_single_required(self.set_register_hive)
        libcontext.socket("register_hive", socket)

        socket = socket_single_required(self.set_get_hive)
        libcontext.socket("get_hive", socket)