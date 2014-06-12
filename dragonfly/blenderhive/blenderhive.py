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


class blenderapp(bee.drone):
    def __init__(self):
        self.startupfunctions = []
        self.cleanupfunctions = []
        self._actors = {}
        self._entities = {}
        self._actorclasses = {}
        self._entityclasses = {}
        self._animationdict = {}
        self.doexit = False
        self._init = False

    def init(self):
        if self._init: return
        self.startupfunctions.sort(key=lambda v: -v[1])
        for f, priority in self.startupfunctions: f()
        self._init = True

    def on_tick(self):
        pass

    def run(self):
        import bge

        bge.render.showMouse(True)
        try:
            self.finished = False
            self.init()
            tickrate = 60.0  # TODO: tick rate locked at 60 now, later: read it from Blender
            t_last_frame = time.time()
            ticks_todo = 0.0
            while not self.doexit:  # TODO: read if Blender one-tick-per-frame option is on, adapt main loop accordingly
                tim = time.time()
                if tim > t_last_frame + 1.0:  #emergency situation; frame rate dropped below 1
                    bge.logic.NextFrame()
                    t_last_frame = time.time()
                    ticks_todo += tickrate * (t_last_frame - tim)

                if ticks_todo > 1:
                    ticks_todo -= 1
                    self.pacemaker.send_input()
                    self.on_tick()
                    self.pacemaker.tick()
                    t = time.time()
                    new_ticks_todo = tickrate * (t - tim)

                    if new_ticks_todo > 0.999: new_ticks_todo = 0.999
                    ticks_todo += new_ticks_todo
                else:
                    bge.logic.NextFrame()
                    self.pacemaker.send_input()
                    t_last_frame = time.time()
                    ticks_todo += tickrate * (t_last_frame - tim)

        finally:
            self.cleanup()
            # ##for now, no difference between actors and entities

    def _register_actor(self, a):
        return self._register_entity(a)

    def _register_actorclass(self, a):
        return self._register_entityclass(a)

    def get_actor_blender(self, actorname, actordict=None):
        return self.get_entity_blender(actorname, actordict)

    def get_actor(self, actorname, actordict=None):
        return self.get_entity(actorname, actordict)

    def get_actorclass(self, actorclassname, actorclassdict=None):
        return self.get_entityclass(actorname, actordict)

    def spawn_actor(self, actorclassname, actorname, actordict=None, entitydict=None, actorclassdict=None):
        return self.spawn_entity(actorclassname, actorname, entitydict, actorclassdict)

    def remove_actor(self, actorname, actordict=None, entitydict=None):
        return self.remove_entity(actorname, entitydict)

    # ##
    """
    def _register_actor(self,a):
      actorname,actor = a
      if actorname in self._actors:
        raise KeyError("Actor '%s' has already been registered" % actorname)
      self._actors[actorname] = actor
    def _register_actorclass(self, a):
      actorclassname, actorclass, nodepath = a
      if actorclassname in self._actorclasses:
        raise KeyError("Actor class '%s' has already been registered" % actorclassname)
      self._actorclasses[actorclassname] = actorclass, nodepath

    def get_actor(self,actorname,actordict=None):
      if actordict is None: actordict=self._actors
      return actordict[actorname]
    def get_actorclass(self,actorclassname,actorclassdict=None):
      #returns actorclass, nodepath
      if actorclassdict is None: actorclassdict = self._actorclasses
      return actorclassdict[actorclassname]

    def spawn_actor(self,actorclassname, actorname,actordict=None,entitydict=None,actorclassdict=None):
      if actordict is None: actordict = self._actors
      if entitydict is None: entitydict = self._entities
      if actorclassdict is None: actorclassdict = self._actorclasses
      #TODO
      \"""
      actorclass, nodepath = actorclassdict[actorclassname]
      actorclass.load()
      if nodepath is not None:
        import copy
        newnodepath = copy.copy(nodepath)
        actorclass.node.reparentTo(newnodepath)
      else:
        newnodepath = actorclass.node
      ent = self.window.render.attachNewNode("")
      newnodepath.reparentTo(ent)
      \"""
      entitydict[actorname] = ent
      actordict[actorname] = actorclass.actor

    def remove_actor(self, actorname,actordict=None,entitydict=None):
      if actordict is None: actordict = self._actors
      if actorname not in actordict:
        raise KeyError("No such actor '%s'" % actorname)
      del actordict[actorname]
      self.remove_entity(actorname,entitydict)
    """

    def _register_entity(self, e):
        entityname, entity = e
        if entityname in self._entities:
            raise KeyError("Entity '%s' has already been registered" % entityname)
        self._entities[entityname] = entity

    def _register_entityclass(self, a):
        entityclassname, entityclass, nodepath = a
        if entityclassname in self._entityclasses:
            raise KeyError("Entity class '%s' has already been registered" % entityclassname)
        self._entityclasses[entityclassname] = (entityclass, nodepath)

    def get_entityclass(self, entityclassname, entityclassdict):
        #returns (entityclass, nodepath)
        if entityclassdict is None: entityclassdict = self._entityclasses
        return entityclassdict[entityclassname]


    def spawn_entity(self, entityclassname, entityname, entitydict=None, entityclassdict=None):
        if entitydict is None: entitydict = self._entities
        if entityclassdict is None: entityclassdict = self._entityclasses
        entityclass, nodepath = entityclassdict[entityclassname]
        scene = self.get_scene()
        ent = scene.addObject(entityclass, entityclass, 0)
        ### TODO: get nodepath correctly; will probably disappear after entity management redesign
        #entitydict[entityname] = ent

        obj = [o for o in scene.objectsInactive if o.name == "Empty_default"][0]
        node0 = scene.addObject(obj, obj, 0)
        ent.setParent(node0)

        entitydict[entityname] = node0


    def remove_entity(self, entityname, entitydict=None):
        if entitydict is None: entitydict = self._entities
        if entityname not in entitydict:
            raise KeyError("No such entity '%s'" % entityname)
        ent = entitydict.pop(entityname)
        ent.endObject()

    def get_entity_blender(self, entityname, entitydict=None, camera=None):
        if camera is None: camera = self.get_camera()
        if entityname is camera: return camera
        if entitydict is None: entitydict = self._entities
        return entitydict[entityname]

    def get_entity(self, entityname, entitydict=None, camera=None):
        from ..scene.matrix import matrix

        ent = self.get_entity_blender(entityname, entitydict, camera)
        return matrix(ent, "Blender")

    def get_entity_axissystem(self, entityname, entitydict=None, camera=None):
        ent = self.get_entity(entityname, entitydict, camera)
        return ent.get_proxy("AxisSystem")

    def get_entity_nodepath(self, entityname, entitydict=None, camera=None):
        ent = self.get_entity(entityname, entitydict, camera)
        return ent.get_proxy("NodePath")

    def entity_parent_to(self, entityname, entityparentname,
                         entitydict=None, camera=None):
        ent = self.get_entity_blender(entityname, entitydict, camera)

        if entityparentname is not None:
            parent = self.get_entity_blender(entityparentname, entitydict, camera)

        loc = ent.localPosition.copy()
        rot = ent.localOrientation.copy()
        if entityparentname is None:
            ent.removeParent()
        else:
            ent.setParent(parent)
        ent.localPosition = loc
        ent.localOrientation = rot

    def entity_unparent(self, entityname):
        self.entity_parent_to(entityname, None)

    def entity_hide(self, entityname, entitydict=None, camera=None):
        ent = self.get_entity_blender(entityname, entitydict, camera)
        ent.setVisible(False, True)

    def entity_show(self, entityname, entitydict=None, camera=None):
        ent = self.get_entity_blender(entityname, entitydict, camera)
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
        self.cleanupfunctions.append(cleanupfunction)

    def cleanup(self):
        if self.finished == False:
            for f in self.cleanupfunctions: f()
        self.finished = True

    def display(self, arg):
        print(arg)

    def watch(self, *args):
        for a in args: print(a, end="")
        print()

    def set_eventfunc(self, eventfunc):
        self.eventfunc = eventfunc

    def set_pacemaker(self, pacemaker):
        self.pacemaker = pacemaker

    def set_get_camera(self, get_camera):
        self.get_camera = get_camera

    def set_get_scene(self, get_scene):
        self.get_scene = get_scene

    def _register_animation(self, animation_name, anim):
        self._animationdict[animation_name] = anim

    def place(self):
        libcontext.socket("startupfunction", socket_container(self.addstartupfunction))
        libcontext.socket("cleanupfunction", socket_container(self.addcleanupfunction))
        libcontext.socket(("evin", "event"), socket_single_required(self.set_eventfunc))

        libcontext.socket(("blender", "register_actor"), socket_container(self._register_actor))
        libcontext.plugin(("blender", "actor-register"), plugin_supplier(self._register_actor))
        libcontext.plugin(("remove", "actor"), plugin_supplier(self.remove_actor))
        libcontext.plugin(("blender", "get_actor"), plugin_supplier(self.get_actor))

        libcontext.socket(("blender", "register_animation"), socket_container(self._register_animation))
        libcontext.plugin(("blender", "animation-register"), plugin_supplier(self._register_animation))

        get_actorfunc = actorwrapper_cache(self.get_actor_blender, self._animationdict)
        libcontext.plugin(("get_actor"), plugin_supplier(get_actorfunc))
        libcontext.socket(("blender", "register_actorclass"), socket_container(self._register_actorclass))
        libcontext.plugin(("blender", "actorclass-register"), plugin_supplier(self._register_actorclass))
        libcontext.plugin(("blender", "get_actorclass"), plugin_supplier(self.get_actorclass))
        libcontext.plugin(("spawn", "actor"), plugin_supplier(self.spawn_actor))

        libcontext.plugin(("blender", "entity-register"), plugin_supplier(self._register_entity))
        libcontext.plugin(("remove", "entity"), plugin_supplier(self.remove_entity))

        libcontext.plugin(("blender", "get_entity"), plugin_supplier(self.get_entity_blender))
        libcontext.plugin("get_entity", plugin_supplier(self.get_entity))
        libcontext.plugin(("get_entity", "Blender"), plugin_supplier(self.get_entity_blender))
        libcontext.plugin(("get_entity", "AxisSystem"), plugin_supplier(self.get_entity_axissystem))
        libcontext.plugin(("get_entity", "NodePath"), plugin_supplier(self.get_entity_nodepath))

        libcontext.socket(("blender", "register_entityclass"), socket_container(self._register_entityclass))
        libcontext.plugin(("blender", "entityclass-register"), plugin_supplier(self._register_entityclass))
        libcontext.plugin(("blender", "get_entityclass"), plugin_supplier(self.get_entityclass))
        libcontext.plugin(("spawn", "entity"), plugin_supplier(self.spawn_entity))

        libcontext.plugin(("entity", "parent_to"), plugin_supplier(self.entity_parent_to))
        libcontext.plugin(("entity", "unparent"), plugin_supplier(self.entity_unparent))
        libcontext.plugin(("entity", "show"), plugin_supplier(self.entity_show))
        libcontext.plugin(("entity", "hide"), plugin_supplier(self.entity_hide))

        libcontext.plugin("exit", plugin_supplier(self.exit))
        libcontext.plugin("stop", plugin_supplier(self.exit))
        libcontext.plugin("display", plugin_supplier(self.display))
        libcontext.plugin("watch", plugin_supplier(self.watch))
        libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
        libcontext.plugin("doexit", plugin_supplier(lambda: getattr(self, "doexit")))

        libcontext.socket("get_camera", socket_single_required(self.set_get_camera))
        libcontext.socket(("blender", "scene"), socket_single_required(self.set_get_scene))


from bee import connect
from ..time import simplescheduler
from ..sys import exitactuator
from ..io import keyboardsensor_trigger
from ..time import pacemaker_simple


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
        if mode == "ping_pong": mode = "pingpong"
        assert mode in ("play", "loop", "pingpong", None), mode

        assert animation_name in self._animationdict, animation_name
        animation = self._animationdict[animation_name]

        if mode is None: mode = animation.play_mode
        import bge

        if mode == "play":
            m = bge.logic.KX_ACTION_MODE_PLAY
        elif mode == "loop":
            m = bge.logic.KX_ACTION_MODE_LOOP
        elif mode == "pingpong":
            m = bge.logic.KX_ACTION_MODE_PING_PONG

        self._blender_actor.playAction(
            animation.name,
            animation.start,
            animation.end,
            animation.layer,
            animation.priority,
            animation.blendin,
            m,
            animation.layer_weight,
            animation.ipo_flags,
            animation.speed
        )
        self._layer = animation.layer

    def stop(self):
        if self._layer is None: return
        self._blender_actor.stopAction(self._layer)
        self._layer = None


class currscene(bee.drone):
    def get_scene(self):
        import bge

        scene = bge.logic.getCurrentScene()
        return scene

    def place(self):
        libcontext.plugin(("blender", "scene"), plugin_supplier(self.get_scene))


from .blenderscene import blenderscene, entityloader, entityclassloader, cameraloader, animationloader


class blenderhive(bee.inithive):
    _hivecontext = hivemodule.appcontext(blenderapp)
    inputhandler = inputhandlerhive()
    connect(("inputhandler", "evout"), "evin")
    scheduler = simplescheduler()
    pacemaker = blenderpacemaker()

    currscene = currscene()
    scene = blenderscene()
    entityloader()
    entityclassloader()
    cameraloader()
    animationloader = animationloader()

    exitactuator = exitactuator()
    keyboardsensor_exit = keyboardsensor_trigger("ESCAPE")
    connect("keyboardsensor_exit", "exitactuator")
