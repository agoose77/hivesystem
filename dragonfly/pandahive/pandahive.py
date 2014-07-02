from __future__ import print_function
import time, functools

import bee
from bee import hivemodule

import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from . import inputhandler
from .pandascene import pandascene
from .pandawindow import pandawindow


class inputhandlerhive(bee.frame):
    inputhandler.inputhandler()


class pandaapp(bee.drone):
    def __init__(self):
        self.startupfunctions = []
        self.cleanupfunctions = []
        self._actors = {}
        self._entities = {}
        self._relmatrices = {}
        self._ref_entities = {}
        self._actorclasses = {}
        self._entityclasses = {}
        self.doexit = False
        self._init = False

    def init(self):
        if self._init: return
        self.camera = self.get_camera()
        for f in self.startupfunctions: f()
        self._init = True

    def on_tick(self):
        pass

    def run(self):
        try:
            self.finished = False
            self.init()
            while not self.doexit:
                self.window.taskMgr.step()
                self.on_tick()
                self.pacemaker.tick()

            self.pacemaker.on_exit()

        finally:
            self.cleanup()

    def _register_actor(self, a):
        actorname, actor = a
        if actorname in self._actors:
            raise KeyError("Actor '%s' has already been registered" % actorname)
        self._actors[actorname] = actor

    def _register_actorclass(self, a):
        actorclassname, actorclass, nodepath = a
        if actorclassname in self._actorclasses:
            raise KeyError("Actor class '%s' has already been registered" % actorclassname)
        self._actorclasses[actorclassname] = actorclass, nodepath

    def get_actor(self, actorname, actordict=None):
        if actordict is None: actordict = self._actors
        return actordict[actorname]

    def get_actorclass(self, actorclassname, actorclassdict=None):
        # returns actorclass, nodepath
        if actorclassdict is None: actorclassdict = self._actorclasses
        return actorclassdict[actorclassname]

    def spawn_actor(self, actorclassname, actorname, actordict=None, entity_dict=None, actorclassdict=None):
        from panda3d.core import NodePath

        if actordict is None: actordict = self._actors
        if entity_dict is None: entity_dict = self._entities
        if actorclassdict is None: actorclassdict = self._actorclasses
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
        entity_dict[actorname] = ent
        actordict[actorname] = actorclass.actor

    def remove_actor(self, actorname, actordict=None, entity_dict=None):
        if actordict is None: actordict = self._actors
        if actorname not in actordict:
            raise KeyError("No such actor '%s'" % actorname)
        del actordict[actorname]
        self.remove_entity(actorname, entity_dict)

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
        # returns (entityclass, nodepath)
        if entityclassdict is None: entityclassdict = self._entityclasses
        return entityclassdict[entityclassname]


    def spawn_entity(self, entityclassname, entityname, entity_dict=None, entityclassdict=None):
        from panda3d.core import NodePath

        if entity_dict is None: entity_dict = self._entities
        if entityclassdict is None: entityclassdict = self._entityclasses
        entityclass, nodepath = entityclassdict[entityclassname]
        entityclass.load()
        if nodepath is not None:
            import copy

            newnodepath = copy.copy(nodepath)
            entityclass.node.reparentTo(newnodepath)
        else:
            newnodepath = entityclass.node
        ent = self.window.render.attachNewNode("")
        newnodepath.reparentTo(ent)
        entity_dict[entityname] = ent

    def remove_entity(self, entityname, entity_dict=None):
        if entity_dict is None: entity_dict = self._entities
        if entityname not in entity_dict:
            raise KeyError("No such entity '%s'" % entityname)
        ent = entity_dict.pop(entityname)
        ent.detachNode()
        if entityname in self._ref_entities: del self._ref_entities[entityname]
        if entityname in self._relmatrices: del self._relmatrices[entityname]

    def get_entity_panda(self, entityname, entity_dict=None, camera=None):
        if camera is None: camera = self.camera
        if entityname is camera: return camera
        if entity_dict is None: entity_dict = self._entities
        return entity_dict[entityname]

    def get_entity(self, entityname, entity_dict=None, camera=None):
        from ..scene.matrix import matrix

        ent = self.get_entity_panda(entityname, entity_dict, camera)
        return matrix(ent, "NodePath")

    def get_entity_view(self, view, entityname, entity_dict=None, camera=None, format="NodePath"):
        import copy
        from panda3d.core import NodePath
        from ..scene.matrix import matrix

        ent = self.get_entity_panda(entityname, entity_dict, camera)
        entmat = matrix(ent, format)
        secondmatrix = None
        if view == "relative":
            if entityname not in self._relmatrices:
                self._relmatrices[entityname] = matrix(copy.copy(ent), "NodePath")
            secondmatrix = self._relmatrices[entityname]
        elif view == "reference":
            try:
                ref_entname = self._ref_entities[entityname]
                ref_ent = self.get_entity_panda(ref_entname, entity_dict)
                secondmatrix = matrix(ref_ent, format)
            except KeyError:
                self._ref_entities[entityname] = entityname
                secondmatrix = entmat
        return entmat.get_view(view, secondmatrix)

    def get_entity_axissystem(self, entityname, entity_dict=None, camera=None):
        ent = self.get_entity(entityname, entity_dict, camera)
        return ent.get_proxy("AxisSystem")

    def entity_parent_to(self, entityname, entityparentname,
                         entity_dict=None, camera=None):
        ent = self.get_entity_panda(entityname, entity_dict, camera)
        parent = self.get_entity_panda(entityparentname, entity_dict, camera)

        ent.reparentTo(parent)

    def entity_hide(self, entityname, entity_dict=None, camera=None):
        ent = self.get_entity_panda(entityname, entity_dict, camera)
        ent.hide()

    def entity_show(self, entityname, entity_dict=None, camera=None):
        ent = self.get_entity_panda(entityname, entity_dict, camera)
        ent.show()

    def exit(self):
        self.doexit = True

    def addstartupfunction(self, startupfunction):
        assert hasattr(startupfunction, "__call__")
        self.startupfunctions.append(startupfunction)

    def addcleanupfunction(self, cleanupfunction):
        assert hasattr(cleanupfunction, "__call__")
        self.cleanupfunctions.append(cleanupfunction)

    def set_window(self, window):
        self.window = window

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

    def place(self):
        libcontext.socket("startupfunction", socket_container(self.addstartupfunction))
        libcontext.socket("cleanupfunction", socket_container(self.addcleanupfunction))
        libcontext.socket(("evin", "event"), socket_single_required(self.set_eventfunc))
        libcontext.socket(("panda", "window"), socket_single_required(self.set_window))

        libcontext.socket(("panda", "register_actor"), socket_container(self._register_actor))
        libcontext.plugin(("panda", "actor-register"), plugin_supplier(self._register_actor))
        libcontext.plugin(("remove", "actor"), plugin_supplier(self.remove_actor))

        libcontext.plugin(("panda", "get_actor"), plugin_supplier(self.get_actor))
        get_actorfunc = functools.partial(get_actorwrapper, self.get_actor)
        libcontext.plugin(("get_actor"), plugin_supplier(get_actorfunc))
        libcontext.socket(("panda", "register_actorclass"), socket_container(self._register_actorclass))
        libcontext.plugin(("panda", "actorclass-register"), plugin_supplier(self._register_actorclass))
        libcontext.plugin(("panda", "get_actorclass"), plugin_supplier(self.get_actorclass))
        libcontext.plugin(("spawn", "actor"), plugin_supplier(self.spawn_actor))

        libcontext.plugin(("panda", "entity-register"), plugin_supplier(self._register_entity))
        libcontext.plugin(("remove", "entity"), plugin_supplier(self.remove_entity))

        libcontext.plugin(("panda", "get_entity"), plugin_supplier(self.get_entity_panda))
        libcontext.plugin("get_entity", plugin_supplier(self.get_entity))
        libcontext.plugin(("get_entity", "NodePath"), plugin_supplier(self.get_entity_panda))
        libcontext.plugin(("get_entity", "AxisSystem"), plugin_supplier(self.get_entity_axissystem))
        for view in ("local", "relative", "reference"):
            libcontext.plugin(("get_entity", "view", view),
                              plugin_supplier(functools.partial(self.get_entity_view, view)))
            libcontext.plugin(("get_entity", "view", view, "NodePath"),
                              plugin_supplier(functools.partial(self.get_entity_view, view)))
            libcontext.plugin(("get_entity", "view", view, "AxisSystem"),
                              plugin_supplier(functools.partial(self.get_entity_view, view, format="AxisSystem")))

        libcontext.socket(("panda", "register_entityclass"), socket_container(self._register_entityclass))
        libcontext.plugin(("panda", "entityclass-register"), plugin_supplier(self._register_entityclass))
        libcontext.plugin(("panda", "get_entityclass"), plugin_supplier(self.get_entityclass))
        libcontext.plugin(("spawn", "entity"), plugin_supplier(self.spawn_entity))

        libcontext.plugin(("entity", "parent_to"), plugin_supplier(self.entity_parent_to))
        libcontext.plugin(("entity", "show"), plugin_supplier(self.entity_show))
        libcontext.plugin(("entity", "hide"), plugin_supplier(self.entity_hide))

        libcontext.plugin("exit", plugin_supplier(self.exit))
        libcontext.plugin("stop", plugin_supplier(self.exit))
        libcontext.plugin("display", plugin_supplier(self.display))
        libcontext.plugin("watch", plugin_supplier(self.watch))
        libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
        libcontext.plugin("doexit", plugin_supplier(lambda: self.doexit))

        libcontext.socket("get_camera", socket_single_required(self.set_get_camera))

        class taskmanagerwrapperclass(object):
            def __getattr__(self, attr): return getattr(self.window.taskMgr, attr)

        taskmanagerwrapper = taskmanagerwrapperclass()
        libcontext.plugin(("panda", "taskmanager"), plugin_supplier(taskmanagerwrapper))


from bee import connect
from ..time import simplescheduler
from ..sys import exitactuator
from ..io import keyboardsensor_trigger
from ..time import pacemaker_simple


def get_actorwrapper(panda_get_actorfunc, actorname):
    return panda_actorwrapper(panda_get_actorfunc(actorname))


class panda_actorwrapper(object):
    def __init__(self, panda_actor):
        self._panda_actor = panda_actor

    def animate(self, animation_name, loop=True):
        assert loop == True  # TODO for non-looping animations
        self._panda_actor.loop(animation_name, restart=False)

    def stop(self):
        self._panda_actor.stop()


class pandahive(bee.inithive):
    _hivecontext = hivemodule.appcontext(pandaapp)
    inputhandler = inputhandlerhive()
    connect(("inputhandler", "evout"), "evin")
    scheduler = simplescheduler()
    exitactuator = exitactuator()
    keyboardsensor_exit = keyboardsensor_trigger("ESCAPE")
    connect("keyboardsensor_exit", "exitactuator")
    scene = pandascene()
    window = pandawindow()
    pacemaker = pacemaker_simple()
