import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from bee.bind import *


class matrix_binder(binderdrone):

    def set_matrix_function(self, function):
        self._get_matrix = function

    def set_matrix_function_nodepath(self, function):
        self._get_matrix_nodepath = function

    def set_matrix_function_axissystem(self, function):
        self._get_matrix_axissystem = function

    def set_matrix_function_blender(self, function):
        self._get_matrix_blender = function

    def bind(self, binderworker, bindname):
        libcontext.plugin(("entity", "bound", "matrix"),
                          plugin_supplier(lambda: self._get_matrix(bindname)))
        libcontext.plugin(("entity", "bound", "matrix", "NodePath"),
                          plugin_supplier(lambda: self._get_matrix_nodepath(bindname)))
        libcontext.plugin(("entity", "bound", "matrix", "AxisSystem"),
                          plugin_supplier(lambda: self._get_matrix_axissystem(bindname)))
        libcontext.plugin(("entity", "bound", "matrix", "Blender"),
                          plugin_supplier(lambda: self._get_matrix_blender(bindname)))
        # TODO: add (unmodified) plugins for ("get_entity", "view", "local") and all other views

    def place(self):
        libcontext.socket("get_entity", socket_single_required(self.set_matrix_function))

        libcontext.socket(("entity", "matrix", "Blender"), socket_single_required(self.set_matrix_function_blender))
        libcontext.socket(("entity", "matrix", "NodePath"), socket_single_required(self.set_matrix_function_nodepath))
        libcontext.socket(("entity", "matrix", "AxisSystem"), socket_single_required(self.set_matrix_function_axissystem))
        # TODO: add sockets for ("get_entity", "view", "local") and all other views


class matrix_binder_view(binderdrone):

    def set_matrix_function(self, function):
        self._get_matrix = function

    def set_matrix_function_nodepath(self, function):
        self._get_matrix_nodepath = function

    def set_matrix_function_axissystem(self, function):
        self._get_matrix_axissystem = function

    def set_matrix_function_blender(self, function):
        self._get_matrix_blender = function

    def bind(self, binderworker, bindname):
        libcontext.plugin(("entity", "bound", "matrix"), plugin_supplier(lambda: self._get_matrix(bindname)))
        libcontext.plugin(("entity", "bound", "matrix", "NodePath"),
                          plugin_supplier(lambda: self._get_matrix_nodepath(bindname)))
        libcontext.plugin(("entity", "bound", "matrix", "AxisSystem"),
                          plugin_supplier(lambda: self._get_matrix_axissystem(bindname)))
        libcontext.plugin(("entity", "bound", "matrix", "Blender"),
                          plugin_supplier(lambda: self._get_matrix_blender(bindname)))
        # TODO: add (unmodified) plugins for ("get_entity", "view", self._view) and all other views

    def place(self):
        libcontext.socket(("entity", "view", self._view), socket_single_required(self.set_matrix_function))
        libcontext.socket(("entity", "view", self._view, "Blender"),
                          socket_single_required(self.set_matrix_function_blender))
        libcontext.socket(("entity", "view", self._view, "NodePath"),
                          socket_single_required(self.set_matrix_function_nodepath))
        libcontext.socket(("entity", "view", self._view, "AxisSystem"),
                          socket_single_required(self.set_matrix_function_axissystem))
        # TODO: add (unmodified) sockets for all other views than ("get_entity", "view", self._view)


class matrix_binder_local(matrix_binder_view):
    _view = "local"


class matrix_binder_relative(matrix_binder_view):
    _view = "relative"


class camera_binder(binderdrone):
    def bind(self, binderworker):
        # ...
        raise Exception("TODO")


class actorbinder(binderdrone):
    def set_actorfunc(self, actorfunc):
        self._get_actor = actorfunc

    def bind(self, binderworker, bindname):
        libcontext.plugin("actor", plugin_supplier(lambda: self._get_actor(bindname)))

    def place(self):
        libcontext.socket("get_actor", socket_single_required(self.set_actorfunc))


class actoroptionalbinder(binderdrone):
    def set_actorfunc(self, actorfunc):
        self._get_actor = actorfunc

    def bind(self, binderworker, bindname):
        try:
            self._get_actor(bindname)
        except KeyError:
            pass
        else:
            libcontext.plugin("actor", plugin_supplier(lambda: self._get_actor(bindname)))

    def place(self):
        libcontext.socket("get_actor", socket_single_required(self.set_actorfunc))


class camerabinder(binderdrone):
    def bind(self, binderworker, bindname):
        libcontext.plugin("entity", plugin_supplier(self.camera))

    def set_camera(self, camera):
        self.camera = camera

    def place(self):
        libcontext.socket("camera", socket_single_required(self.set_camera))


class entitybridge(binderdrone):
    def bind(self, binderworker):
        # ...
        raise Exception("TODO")


class entityclassonlybridge(binderdrone):
    def bind(self, binderworker):
        # ...
        raise Exception("TODO")


class entityclear(binderdrone):
    def bind(self, binderworker):
        # ...
        raise Exception("TODO")


class entity_binder(binderdrone):

    def set_set_parent(self, set_parent):
        self.set_parent = set_parent

    def set_remove_parent(self, remove_parent):
        self.remove_parent = remove_parent

    def set_set_property(self, set_property):
        self.set_property = set_property

    def set_get_property(self, get_property):
        self.get_property = get_property

    def set_get_collisions(self, get_collisions):
        self.get_collisions = get_collisions

    def set_show(self, show):
        self.show = show

    def set_hide(self, hide):
        self.hide = hide

    def set_get_material(self, get_material):
        self.get_material = get_material

    def set_remove_entity(self, remove_entity):
        self.remove_entity = remove_entity

    def set_get_entity(self, get_entity):
        self.get_entity = get_entity

    def set_stop_func(self, stop_func):
        self.stop_func = stop_func

    def set_entity_register_process(self, function):
        self.entity_register_process = function

    def bind(self, bind_worker, bindname):
        """Bind call to map plugins to bound hive

        :param bind_worker: worker instance used for binding
        :param bindname: name of bound entity (Warning, this is passed by keyword)
        """
        # Bound functions
        # TODO just pass string here
        libcontext.plugin(("entity", "bound"), plugin_supplier(lambda: bindname))
        libcontext.plugin(("entity", "bound", "parent", "set"),
                          plugin_supplier(lambda parent: self.set_parent(bindname, parent)))
        libcontext.plugin(("entity", "bound", "parent", "remove"),
                          plugin_supplier(lambda: self.remove_parent(bindname)))
        libcontext.plugin(("entity", "bound", "property", "set"),
                          plugin_supplier(lambda name, value: self.set_property(bindname, name, value)))
        libcontext.plugin(("entity", "bound", "property", "get"),
                          plugin_supplier(lambda name: self.get_property(bindname, name)))
        libcontext.plugin(("entity", "bound", "material", "get"),
                          plugin_supplier(lambda name: self.get_material(bindname, name)))
        libcontext.plugin(("entity", "bound", "collisions"), plugin_supplier(lambda: self.get_collisions(bindname)))
        libcontext.plugin(("entity", "bound", "remove"), plugin_supplier(lambda: self.remove_entity(bindname)))

        # Unbound functions
        libcontext.plugin(("entity", "parent", "set"), plugin_supplier(self.set_parent))
        libcontext.plugin(("entity", "parent", "remove"), plugin_supplier(self.remove_parent))
        libcontext.plugin(("entity", "property", "set"), plugin_supplier(self.set_property))
        libcontext.plugin(("entity", "property", "get"), plugin_supplier(self.get_property))
        libcontext.plugin(("entity", "material", "get"), plugin_supplier(self.get_material))
        libcontext.plugin(("entity", "collisions"), plugin_supplier(self.get_collisions))
        libcontext.plugin(("entity", "remove"), plugin_supplier(self.remove_entity))
        libcontext.plugin(("entity", "get"), plugin_supplier(self.get_entity))

    def place(self):
        libcontext.socket(("entity", "parent", "set"), socket_single_required(self.set_set_parent))
        libcontext.socket(("entity", "parent", "remove"), socket_single_required(self.set_remove_parent))
        libcontext.socket(("entity", "show"), socket_single_required(self.set_show))
        libcontext.socket(("entity", "hide"), socket_single_required(self.set_hide))
        libcontext.socket(("entity", "property", "get"), socket_single_required(self.set_get_property))
        libcontext.socket(("entity", "property", "set"), socket_single_required(self.set_set_property))
        libcontext.socket(("entity", "collisions"), socket_single_required(self.set_get_collisions))
        libcontext.socket(("entity", "material", "get"), socket_single_required(self.set_get_material))
        libcontext.socket(("entity", "remove"), socket_single_required(self.set_remove_entity))
        libcontext.socket(("entity", "get"), socket_single_required(self.set_get_entity))


class bind(bind_baseclass):
    bind_matrix = bindparameter(True)
    binder("bind_matrix", False, None)
    binder("bind_matrix", True, matrix_binder(), "bindname")  # the matrix of the entity
    binder("bind_matrix", "local", matrix_binder_local(), "bindname")
    binder("bind_matrix", "relative", matrix_binder_relative(), "bindname")
    # TODO
    binder("bind_matrix", "camera", camera_binder())

    bind_entity = bindparameter(True)
    binder("bind_entity", True, entity_binder(), "bindname")

    bind_actor = bindparameter("optional")
    binder("bind_actor", False, None)
    binder("bind_actor", "optional", actoroptionalbinder(), "bindname")
    binder("bind_actor", True, actorbinder(), "bindname")

    bind_camera = bindparameter("transmit")
    binder("bind_camera", False, None)
    binder("bind_camera", "transmit", pluginbridge("camera"))
    binder("bind_camera", "transmit", pluginbridge("get_camera"))
    binder("bind_camera", "entity", camerabinder(), "bindname")

    bind_spawn = bindparameter(True)
    binder("bind_spawn", True, pluginbridge(("spawn", "entity")))

    bind_collision_api = bindparameter(True)
    binder("bind_collision_api", True, pluginbridge(("collision", "contact_test")))
    binder("bind_collision_api", True, pluginbridge(("collision", "create_node", "sphere")))

    entitydata = bindparameter(None)  # also for actors and entity/actorclasses!
    binder("entitydata", None, None)
    binder("entitydata", "transmit", entitybridge())  # also bridges spawning and classes
    binder("entitydata", "class-only",
           entityclassonlybridge())  # clears entity_dict and actordict, but maintains the classes
    binder("entitydata", "clear",
           entityclear())  #clears entity_dict and actordict and removes entityclasses and actorclasses
