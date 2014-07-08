import bee
import libcontext
import Spyder
from bee.spyderhive.hivemaphive import hivemapinithive

from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class entitybinderdrone(bee.drone):

    """Provides plugins for scene-object binding on startup"""

    def get_registered_hivemap_name(self, entity_name):
        """Find hivemap for entity, and register it if not already registered.

        Return the hivemap name

        :param entity_name: name of entity
        """
        try:
            hivemap_name = self.get_property(entity_name, "hivemap")

        except KeyError:
            return None

        try:
            hive_cls = self.get_func(hivemap_name)

        except KeyError:
            hivemap_ = Spyder.Hivemap.fromfile(hivemap_name)
            wrapper_hive = type("WrapperHive", (hivemapinithive,), dict(hivemap=hivemap_))
            self.register_func(hivemap_name, wrapper_hive)

        return hivemap_name

    def set_get_entity(self, plugin):
        self.get_entity = plugin

    def set_get_property(self, plugin):
        self.get_property = plugin

    def set_register_hive(self, register_func):
        self.register_func = register_func

    def set_get_hive(self, get_func):
        self.get_func = get_func

    def place(self):
        binder_plugin = plugin_single_required(self.get_registered_hivemap_name)
        libcontext.plugin(("entity", "get_registered_hivemap_name"), binder_plugin)

        socket = socket_single_required(self.set_get_property)
        libcontext.socket(("entity", "property", "get"), socket)

        socket = socket_single_required(self.set_register_hive)
        libcontext.socket("register_hive", socket)

        socket = socket_single_required(self.set_get_hive)
        libcontext.socket("get_hive", socket)