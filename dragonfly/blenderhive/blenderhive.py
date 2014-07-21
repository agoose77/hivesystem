from __future__ import print_function
import time, functools

import bee
from bee import hivemodule, event

import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from .inputhandler import inputhandler


class inputhandlerhive(bee.frame):
    inputhandler()


# noinspection PyCompatibility
class blenderapp(bee.drone):

    def __init__(self):
        self.startupfunctions = []
        self.cleanup_functions = []
        self._actors = {}
        self._entities = {}
        self._entity_names = {}
        self._actorclasses = {}
        self._relmatrices = {}
        self._ref_entities = {}
        self._entity_classes = {}
        self._animationdict = {}

        self._collision_dict = {}
        self._collision_callback_dict = {}

        self.doexit = False
        self._init = False

    def init(self):
        if self._init:
            return

        self.startupfunctions.sort(key=lambda func_and_priority: -func_and_priority[1])
        for function, priority in self.startupfunctions:
            function()

        self._init = True

    def on_tick(self):
        self.update_entity_collisions()

    def run(self):
        import bge

        bge.render.showMouse(True)
        try:
            self.finished = False
            self.init()
            tick_rate = bge.logic.getLogicTicRate()
            last_time = time.time()
            accumulator = 0.0

            while not self.doexit:  # TODO: read if Blender one-tick-per-frame option is on, adapt main loop accordingly
                current_time = time.time()
                if current_time > last_time + 1.0:  #emergency situation; frame rate dropped below 1
                    bge.logic.NextFrame()
                    last_time = time.time()
                    accumulator += tick_rate * (last_time - current_time)

                if accumulator > 1:
                    accumulator -= 1
                    self.pacemaker.send_input()
                    self.on_tick()
                    self.pacemaker.tick()
                    t = time.time()
                    new_ticks_todo = tick_rate * (t - current_time)

                    if new_ticks_todo > 0.999:
                        new_ticks_todo = 0.999
                    accumulator += new_ticks_todo

                else:
                    bge.logic.NextFrame()
                    self.pacemaker.send_input()
                    last_time = time.time()
                    accumulator += tick_rate * (last_time - current_time)

            self.pacemaker.on_exit()

        finally:
            self.cleanup()
            # ##for now, no difference between actors and entities

    def _register_actor(self, a):
        return self._register_entity(a)

    def _register_actor_class(self, a):
        return self._register_entity_class(a)

    def get_actor_blender(self, actorname, actordict=None):
        return self.get_entity_blender(actorname, actordict)

    def get_actor(self, actorname, actordict=None):
        return self.get_entity(actorname, actordict)

    def get_actor_class(self, actorclassname, actor_class_dict=None):
        return self.get_entityclass(actorclassname, actor_class_dict)

    def spawn_actor(self, actor_class_name, actor_name, actor_dict=None, entity_dict=None, actor_class_dict=None):
        return self.spawn_entity(actor_class_name, actor_name, entity_dict, actor_class_dict)

    def remove_actor(self, actor_name, actor_dict=None, entity_dict=None):
        return self.remove_entity(actor_name, entity_dict)

    def _register_entity(self, entity_data):
        """Register entity to the scene

        :param entity_data: tuple of entity name, entity object
        """
        entity_name, entity = entity_data
        if entity_name in self._entities:
            raise KeyError("Entity '%s' has already been registered" % entity_name)

        self._entities[entity_name] = entity
        self._entity_names[entity] = entity_name
        self._register_entity_collisions(entity_name)

    # TODO determine nodepath
    def _register_entity_class(self, entity_class_data):
        """Register entity class to the scene

        :param entity_class_data: tuple of entity class name, entity class object
        """
        entity_class_name, entity_class, nodepath = entity_class_data
        if entity_class_name in self._entity_classes:
            raise KeyError("Entity class '%s' has already been registered" % entity_class_name)

        self._entity_classes[entity_class_name] = (entity_class, nodepath)

    def _register_entity_collisions(self, entity_name):
        """Register collision callbacks for entity

        :param entity_name: name of entity
        """
        entity = self.get_entity_blender(entity_name)

        collisions_list = []
        collision_callback = functools.partial(self.handle_entity_collision, entity, collisions_list)
        #TODO temporary check
        import bge
        if hasattr(bge.types.KX_GameObject, "collisionCallbacks"):
            entity.collisionCallbacks.append(collision_callback)

        self._collision_callback_dict[entity_name] = collision_callback
        self._collision_dict[entity_name] = collisions_list

    def get_entity_class(self, entityclassname, entityclassdict):
        #returns (entityclass, nodepath)
        if entityclassdict is None:
            entityclassdict = self._entity_classes

        return entityclassdict[entityclassname]

    def spawn_entity(self, entityclassname, entityname, entity_dict=None, entityclassdict=None):
        if entity_dict is None:
            entity_dict = self._entities

        if entityclassdict is None:
            entityclassdict = self._entity_classes

        entityclass, nodepath = entityclassdict[entityclassname]
        scene = self.get_scene()
        ent = scene.addObject(entityclass, entityclass, 0)
        ### TODO: get nodepath correctly; will probably disappear after entity management redesign
        #entity_dict[entityname] = ent

        # TODO handle necessary spawn object
        obj = [o for o in scene.objectsInactive if o.name == "Empty_default"][0]
        node0 = scene.addObject(obj, obj, 0)
        ent.setParent(node0)

        entity_dict[entityname] = node0

    def remove_entity(self, entity_name, entity_dict=None, name_dict=None, end_process=True):
        if entity_dict is None:
            entity_dict = self._entities

        if name_dict is None:
            name_dict = self._entity_names

        if entity_name not in entity_dict:
            raise KeyError("No such entity '%s'" % entity_name)

        # Process management cleanup
        self.stop_process(entity_name)

        entity = entity_dict.pop(entity_name)
        name_dict.pop(entity)
        entity.endObject()

        if entity_name in self._ref_entities:
            del self._ref_entities[entity_name]

        if entity_name in self._relmatrices:
            del self._relmatrices[entity_name]

    def get_entity_blender(self, entityname, entity_dict=None, camera=None):
        #TODO question this logic
        if camera is None:
            camera = self.get_camera()

        if entityname is camera:
            return camera

        if entity_dict is None:
            entity_dict = self._entities

        return entity_dict[entityname]

    def get_entity_names(self, entity_dict=None):
        if entity_dict is None:
            entity_dict = self._entities

        return list(entity_dict.keys())

    def get_entity(self, entityname, entity_dict=None, camera=None):
        from ..scene.matrix import matrix

        ent = self.get_entity_blender(entityname, entity_dict, camera)
        return matrix(ent, "Blender")

    def get_entity_axissystem(self, entityname, entity_dict=None, camera=None):
        ent = self.get_entity(entityname, entity_dict, camera)
        return ent.get_proxy("AxisSystem")

    def get_entity_nodepath(self, entityname, entity_dict=None, camera=None):
        ent = self.get_entity(entityname, entity_dict, camera)
        return ent.get_proxy("NodePath")

    def get_entity_view(self, view, entity_name, entity_dict=None, camera=None, format="Blender"):
        from ..scene.matrix import matrix
        from ..scene.matrixview import KX_GameObject_HiveProxy
        ent = self.get_entity_blender(entity_name, entity_dict, camera)
        entmat = matrix(ent, format)
        secondmatrix = None

        if view == "relative":
            if entity_name not in self._relmatrices:
                rel = KX_GameObject_HiveProxy(ent.localOrientation, ent.localPosition)
                self._relmatrices[entity_name] = matrix(rel, "Blender")
            secondmatrix = self._relmatrices[entity_name]

        elif view == "reference":
            try:
                ref_entname = self._ref_entities[entity_name]
                ref_ent = self.get_entity_blender(ref_entname,entity_dict)
                secondmatrix = matrix(ref_ent, format)
            except KeyError:
                self._ref_entities[entity_name] = entity_name
                secondmatrix = entmat

        return entmat.get_view(view, secondmatrix)

    def entity_get_collisions(self, entity_name, entity_dict=None, camera=None):
        return [collision_info[1] for collision_info in self._collision_dict[entity_name]]

    def entity_get_property(self, entity_name, property_name, entity_dict=None):
        """Get property from entity

        :param entity_name: name of entity
        :param property_name: name of property
        """
        entity = self.get_entity_blender(entity_name, entity_dict=entity_dict)
        return entity[property_name]

    def entity_set_property(self, entity_name, property_name, property_value, entity_dict=None):
        """Set property on entity

        :param entity_name: name of entity
        :param property_name: name of property
        :param property_value: value of property
        """
        entity = self.get_entity_blender(entity_name, entity_dict=entity_dict)
        entity[property_name] = property_value

    def entity_get_material(self, entity_name, material_name, entity_dict=None):
        """Get material from entity

        :param entity_name: name of entity
        :param material_name: name of material
        """
        #TODO add material proxy
        entity = self.get_entity_blender(entity_name, entity_dict=entity_dict)
        name_to_material = {mesh.getMaterialName(material.material_index) for mesh in entity.meshes
                            for material in mesh.materials}
        return name_to_material[material_name]

    def entity_parent_to(self, entity_name, entity_parent_name, entity_dict=None, camera=None):
        ent = self.get_entity_blender(entity_name, entity_dict, camera)

        if entity_parent_name is not None:
            parent = self.get_entity_blender(entity_parent_name, entity_dict, camera)

        loc = ent.localPosition.copy()
        rot = ent.localOrientation.copy()
        if entity_parent_name is None:
            ent.removeParent()
        else:
            ent.setParent(parent)
        ent.localPosition = loc
        ent.localOrientation = rot

    def entity_unparent(self, entityname):
        self.entity_parent_to(entityname, None)

    def entity_hide(self, entityname, entity_dict=None, camera=None):
        ent = self.get_entity_blender(entityname, entity_dict, camera)
        ent.setVisible(False, True)

    def entity_show(self, entityname, entity_dict=None, camera=None):
        ent = self.get_entity_blender(entityname, entity_dict, camera)
        ent.setVisible(True, True)

    def exit(self):
        self.doexit = True

    def addstartupfunction(self, startupfunction):
        if isinstance(startupfunction, tuple):
            sf, priority = startupfunction
        else:
            sf, priority = startupfunction, 0
        assert hasattr(sf, "__call__")
        self.startupfunctions.append((sf, priority))

    def addcleanupfunction(self, cleanupfunction):
        assert hasattr(cleanupfunction, "__call__")
        self.cleanup_functions.append(cleanupfunction)

    def cleanup(self):
        if not self.finished:
            for func in self.cleanup_functions:
                func()

        self.finished = True

    def display(self, arg):
        print(arg)

    def watch(self, *args):
        for a in args:
            print(a, end="")
        print()

    def set_eventfunc(self, eventfunc):
        self.event_func = eventfunc

    def set_pacemaker(self, pacemaker):
        self.pacemaker = pacemaker

    def set_get_camera(self, get_camera):
        self.get_camera = get_camera

    def set_get_scene(self, get_scene):
        self.get_scene = get_scene

    def _register_animation(self, animation_name, anim):
        self._animationdict[animation_name] = anim

    def handle_entity_collision(self, entity, collisions_list, other_entity):
        """Callback when BGE collision is processed

        :param entity: entity callback belongs to
        :param collisions_list: list of current collisions
        :param other_entity: other entity we collided with
        """
        collision_tagged = True
        other_entity_name = self._entity_names[other_entity]
        collision_info = [collision_tagged, other_entity_name]
        collisions_list.append(collision_info)

    def update_entity_collisions(self):
        """Remove untagged collisions from the currently managed collisions"""
        for entity, collision_list in self._collision_dict.items():
            ended_collisions = []

            for collision_info in collision_list:
                collision_set, collision = collision_info

                if not collision_set:
                    ended_collisions.append(collision_info)

                else:
                    collision_info[0] = False

            for collision_info in ended_collisions:
                collision_list.remove(collision_info)

    def set_stop_process(self, stop_process):
        self.stop_process = stop_process

    def get_hivemap_name_for_entity(self, entity_name):
        return self._entities[entity_name]["hivemap"]

    def get_hivemap_name_for_entity_class(self, entity_class_name):
        return self._entity_classes[entity_class_name][0]["hivemap"]

    def place(self):
        libcontext.socket("startupfunction", socket_container(self.addstartupfunction))
        libcontext.socket("cleanupfunction", socket_container(self.addcleanupfunction))
        libcontext.socket(("evin", "event"), socket_single_required(self.set_eventfunc))

        # Registration accessors
        libcontext.socket(("blender", "register_actor"), socket_container(self._register_actor))
        libcontext.plugin(("blender", "actor-register"), plugin_supplier(self._register_actor))
        libcontext.plugin(("remove", "actor"), plugin_supplier(self.remove_actor))
        libcontext.plugin(("blender", "get_actor"), plugin_supplier(self.get_actor))

        libcontext.socket(("blender", "register_animation"), socket_container(self._register_animation))
        libcontext.plugin(("blender", "animation-register"), plugin_supplier(self._register_animation))

        get_actorfunc = actorwrapper_cache(self.get_actor_blender, self._animationdict)
        libcontext.plugin(("get_actor"), plugin_supplier(get_actorfunc))
        libcontext.socket(("blender", "register_actorclass"), socket_container(self._register_actor_class))
        libcontext.plugin(("blender", "actorclass-register"), plugin_supplier(self._register_actor_class))
        libcontext.plugin(("blender", "get_actorclass"), plugin_supplier(self.get_actor_class))
        libcontext.plugin(("spawn", "actor"), plugin_supplier(self.spawn_actor))

        libcontext.plugin(("blender", "entity-register"), plugin_supplier(self._register_entity))
        libcontext.plugin(("entity", "remove"), plugin_supplier(self.remove_entity))

        # Matrix methods
        libcontext.plugin(("entity", "matrix",), plugin_supplier(self.get_entity))
        libcontext.plugin(("entity", "matrix", "Blender"), plugin_supplier(self.get_entity_blender))
        libcontext.plugin(("entity", "matrix", "AxisSystem"), plugin_supplier(self.get_entity_axissystem))
        libcontext.plugin(("entity", "matrix", "NodePath"), plugin_supplier(self.get_entity_nodepath))

        for view in ("local", "relative", "reference"):
            libcontext.plugin(("entity", "view", view),
                              plugin_supplier(functools.partial(self.get_entity_view, view)))
            libcontext.plugin(("entity", "view", view, "Blender"),
                              plugin_supplier(functools.partial(self.get_entity_view, view)))
            libcontext.plugin(("entity", "view", view, "NodePath"),
                              plugin_supplier(functools.partial(self.get_entity_view, view, format="NodePath")))
            libcontext.plugin(("entity", "view", view, "AxisSystem"),
                              plugin_supplier(functools.partial(self.get_entity_view, view, format="AxisSystem")))

        libcontext.socket(("blender", "register_entityclass"), socket_container(self._register_entity_class))
        libcontext.plugin(("blender", "entityclass-register"), plugin_supplier(self._register_entity_class))
        libcontext.plugin(("blender", "get_entityclass"), plugin_supplier(self.get_entity_class))
        libcontext.plugin(("entity", "spawn"), plugin_supplier(self.spawn_entity))

        # Get entity class
        libcontext.plugin(("entity", "class"), plugin_supplier(self.get_entity_class))
        libcontext.plugin(("entity", "class", "blender"), plugin_supplier(self.get_entity_class))

        # Entity accessors
        libcontext.plugin(("entity", "get"), plugin_supplier(self.get_entity_blender))
        libcontext.plugin(("entity", "get", "Blender"), plugin_supplier(self.get_entity_blender))


        # Get entity names
        libcontext.plugin(("entity", "names"), plugin_supplier(self.get_entity_names))

        # Get bound hivemaps
        libcontext.plugin(("entity", "hivemap"), plugin_supplier(self.get_hivemap_name_for_entity))
        libcontext.plugin(("entity", "class", "hivemap"), plugin_supplier(self.get_hivemap_name_for_entity_class))

        # Entity methods
        libcontext.plugin(("entity", "parent", "set"), plugin_supplier(self.entity_parent_to))
        libcontext.plugin(("entity", "parent", "remove"), plugin_supplier(self.entity_unparent))
        libcontext.plugin(("entity", "show"), plugin_supplier(self.entity_show))
        libcontext.plugin(("entity", "hide"), plugin_supplier(self.entity_hide))
        libcontext.plugin(("entity", "property", "get"), plugin_supplier(self.entity_get_property))
        libcontext.plugin(("entity", "property", "set"), plugin_supplier(self.entity_set_property))
        libcontext.plugin(("entity", "collisions"), plugin_supplier(self.entity_get_collisions))
        libcontext.plugin(("entity", "material", "get"), plugin_supplier(self.entity_get_material))

        # System methods
        libcontext.plugin("exit", plugin_supplier(self.exit))
        libcontext.plugin("stop", plugin_supplier(self.exit))
        libcontext.plugin("display", plugin_supplier(self.display))
        libcontext.plugin("watch", plugin_supplier(self.watch))
        libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
        libcontext.socket(("process", "stop"), socket_single_required(self.set_stop_process))

        # TODO remove or rename
        libcontext.plugin("doexit", plugin_supplier(lambda: self.doexit))

        libcontext.socket("get_camera", socket_single_required(self.set_get_camera))
        libcontext.socket(("blender", "scene"), socket_single_required(self.set_get_scene))


from bee import connect
from ..time import simplescheduler
from ..sys import exitactuator
from ..io import keyboardsensor_trigger, messagehandler
from ..time import pacemaker_simple
from ..sys import processmanager


class blenderpacemaker(pacemaker_simple):

    def send_input(self):
        self.eventfunc(bee.event("send_input"))


class actorwrapper_cache(object):
    def __init__(self, blender_get_actorfunc, animationdict):
        self.blender_get_actorfunc = blender_get_actorfunc
        self.animationdict = animationdict
        self.cache = {}

    def __call__(self, actorname):
        if actorname not in self.cache:
            a = blender_actorwrapper(self.blender_get_actorfunc(actorname), self.animationdict)
            self.cache[actorname] = a
        return self.cache[actorname]


class blender_actorwrapper(object):
    def __init__(self, blender_actor, animationdict):
        self._blender_actor = blender_actor
        self._animationdict = animationdict
        self._layer = None

    def animate(self, animation_name, loop=None, mode=None):
        if self._layer is not None:
            self.stop()

        assert loop is None or mode is None
        if loop == False:
            mode = "play"

        elif loop == True:
            mode = "loop"

        if mode == "ping_pong":
            mode = "pingpong"

        assert mode in ("play", "loop", "pingpong", None), mode
        assert animation_name in self._animationdict, animation_name
        animation = self._animationdict[animation_name]

        if mode is None:
            mode = animation.play_mode

        import bge

        if mode == "play":
            bge_mode = bge.logic.KX_ACTION_MODE_PLAY

        elif mode == "loop":
            bge_mode = bge.logic.KX_ACTION_MODE_LOOP

        elif mode == "pingpong":
            bge_mode = bge.logic.KX_ACTION_MODE_PING_PONG

        self._blender_actor.playAction(
            animation.name,
            animation.start,
            animation.end,
            animation.layer,
            animation.priority,
            animation.blendin,
            bge_mode,
            animation.layer_weight,
            animation.ipo_flags,
            animation.speed
        )
        self._layer = animation.layer

    def stop(self):
        if self._layer is None:
            return

        self._blender_actor.stopAction(self._layer)
        self._layer = None


class current_scene(bee.drone):

    def get_scene(self):
        import bge

        scene = bge.logic.getCurrentScene()
        return scene

    def place(self):
        libcontext.plugin(("blender", "scene"), plugin_supplier(self.get_scene))


from .blenderscene import blenderscene, entityloader, entityclassloader, cameraloader, animationloader
from .near_drone import near_drone


class blenderhive(bee.inithive):
    _hivecontext = hivemodule.appcontext(blenderapp)

    inputhandler = inputhandlerhive()
    connect(("inputhandler", "evout"), "evin")
    scheduler = simplescheduler()
    pacemaker = blenderpacemaker()

    currscene = current_scene()
    scene = blenderscene()
    entityloader()
    entityclassloader()
    cameraloader()
    animationloader = animationloader()
    processmanager = processmanager()
    messagehandler = messagehandler()

    near_drone = near_drone()

    exitactuator = exitactuator()
    # TODO read key from API
    keyboardsensor_exit = keyboardsensor_trigger("ESCAPE")
    connect("keyboardsensor_exit", "exitactuator")