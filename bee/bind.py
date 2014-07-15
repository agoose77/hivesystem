# a worker factory class
# the worker has input "bind" (taking a tuple containing the bindantenna parameters)
# "pause"/"resume" (to control the eventmatcher taking keyboard/mouse events; the eventmatcher also checks that the bound hive has not been stopped)
#  "stop" (taking a bindname), which ends the event dispatching and tick listening
#  and "event". 
# automatically catches the exceptions in the bound hive, similar as a hive would do with its workers and drones
#There is always at least one bindantenna "bindname"

#if you inherit from a bindclass that has "x = bindparameter(...)",
# you can say "x = True" and it will be interpreted as "x = bindparameter(True)"
# this means that you cannot delete bindparameters and binders in derived classes 

from __future__ import print_function
import libcontext
from .segments import *
from . import worker, drone
from .bindworker import bindworker
from . import connect as hiveconnect
import inspect

from .types import _types as types
from .raiser import raiser


def get_reg_bindhelper(fr, dicvalues):
    from .hivemodule import allreg

    for d in dicvalues:
        try:
            allreg.add(d)

        except TypeError:  #cannot weakref everything
            pass
    ret = []
    if fr in reg_bindhelper.reg:
        for a in reg_bindhelper.reg[fr]:
            if a in allreg:
                continue
            allreg.add(a)
            ret.append(a)
        del reg_bindhelper.reg[fr]

    return ret


from . import mytype


class bindbuilder(mytype):

    def __new__(metacls, name, bases, cls_dict):
        if name.endswith("bind_baseclass"):
            return mytype.__new__(metacls, name, bases, cls_dict)

        new_cls_dict = {"bindname": bindantenna("id")}

        bindhelpers_nameless = []
        for cls in bases:
            for bind_helper in getattr(cls, "__bindhelpers__", ()):
                if bind_helper not in bindhelpers_nameless:
                    bindhelpers_nameless.append(bind_helper)

        for cls in reversed(bases):
            new_cls_dict.update(cls.__dict__)

        oldbindparameters = {}
        for k in new_cls_dict:
            if isinstance(new_cls_dict[k], bindparameter): oldbindparameters[k] = new_cls_dict[k]
        new_cls_dict.update(cls_dict)

        fr = id(inspect.currentframe().f_back)
        bindhelpers_nameless += get_reg_bindhelper(fr, new_cls_dict.values())
        new_cls_dict["__bindhelpers__"] = bindhelpers_nameless
        bindhelpers = []
        rdkeys = new_cls_dict.keys()
        for k in sorted(rdkeys):
            a = new_cls_dict[k]
            if isinstance(a, bindhelper):
                bindhelpers.append((k, a))
        bindparameters = [h for h in bindhelpers if isinstance(h[1], bindparameter)]

        dicitems = [(k, cls_dict[k]) for k in sorted(cls_dict.keys())]
        morebindparameters = [(h[0], bindparameter(h[1])) for h in dicitems if
                              h not in bindparameters and h[0] in oldbindparameters]
        bindparameters += morebindparameters
        bindparameternames = set([h[0] for h in bindparameters])

        bindhelpers.sort(key=lambda n: n[0])

        bindantennas = [n for n in bindhelpers if isinstance(n[1], bindantenna)]
        bindantennatypes = tuple([b[1].type for b in bindantennas])
        for t in bindantennatypes:
            assert t in types, t

        if len(bindantennatypes) == 1:
            bindantennatypes = bindantennatypes[0]

        bindhelpers += [((nr + 1), a) for nr, a in enumerate(bindhelpers_nameless)]

        binders = [n[1] for n in bindhelpers if isinstance(n[1], binder)]
        for cls in binders:
            assert cls.parameter_name in bindparameternames, cls.parameter_name

        prebinders = [n[1] for n in bindhelpers if isinstance(n[1], prebinder)]

        def get_bindhiveworker(*args, **kwargs):
            class bindhiveworker(bindworker):
                __beename__ = name + "-worker"
                bindworkerhive = new_cls_dict["hive"]

                class propclass(object):
                    def __init__(self, value):
                        self.value = value

                    def get(self, instance):
                        try:
                            ret = instance.value
                            if isinstance(ret, tuple) and len(ret) == 2 and ret[-1] == "value":
                                raise AttributeError
                        except AttributeError:
                            return self.value

                    def set(self, instance, value):
                        instance.value = value

                p = None
                for p in bindparameters:
                    locals()[p[0]] = p[1].value  #changes can only be made by subclassing
                del p

                bind = antenna("push", bindantennatypes)
                v_bind = variable(bindantennatypes)
                connect(bind, v_bind)

                def on_place(self):
                    for binder_ in self.binder_instances:
                        if getattr(self, binder_.parameter_name) != binder_.parameter_value:
                            continue

                        values = {}
                        for antenna_name in binder_.antenna_names:
                            values[antenna_name] = self.bindantennavalues[antenna_name]

                        binder_.binder_drone_instance.bind(self, **values)

                @modifier
                def parse_bindantennas(self):
                    vb = self.v_bind
                    if len(bindantennas) == 1: vb = (vb,)
                    self.bindantennavalues = {}
                    for name, value in zip(bindantennas, vb):
                        self.bindantennavalues[name[0]] = value

                    for prebinder in self.pre_binder_instances:
                        values = {}
                        for antennaname in prebinder.antennanames:
                            values[antennaname] = self.bindantennavalues[antennaname]
                        prebinder.binder_drone_instance.bind(self, **values)

                @modifier
                def do_bind(self):
                    if self.hive is None:
                        raise ValueError('"hive" is not defined in bind class "%s"' % name)

                    bind_name = self.bindantennavalues["bindname"]

                    class bindbridge(drone):

                        def __init__(bridge):
                            bridge.startup_functions = []
                            bridge.cleanup_functions = []

                        def place(bridge):
                            self.on_place()

                            # Expose these to the hive, per class
                            s = libcontext.socketclasses.socket_supplier(bridge.startup_functions.append)
                            libcontext.socket("startupfunction", s)

                            s = libcontext.socketclasses.socket_supplier(bridge.cleanup_functions.append)
                            libcontext.socket("cleanupfunction", s)


                    class newhive(self.hive):
                        zzz_bindbridgedrone = bindbridge()
                        raiser = raiser()
                        hiveconnect("evexc", raiser)

                    hive = newhive().getinstance()
                    try:
                        libcontext.push(self._context.contextname)
                        hive.build(bind_name)
                        hive.place()

                    finally:
                        libcontext.pop()

                    hive.close()
                    hive.init()

                    for function in newhive.zzz_bindbridgedrone.startup_functions:
                        function()

                    self.hives[bind_name] = hive

                trigger(v_bind, parse_bindantennas)
                trigger(v_bind, do_bind)

                # Pause name
                pause = antenna("push", "id")
                v_pause = variable("id")
                connect(pause, v_pause)

                @modifier
                def m_pause(self):
                    paused_name = self.v_pause
                    self.handler_states[paused_name] = False

                trigger(v_pause, m_pause)

                # Resume name
                resume = antenna("push", "id")
                v_resume = variable("id")
                connect(resume, v_resume)

                @modifier
                def m_resume(self):
                    resumed_name = self.v_resume
                    self.handler_states[resumed_name] = True

                trigger(v_resume, m_resume)

                # Stop all hives
                @modifier
                def m_stop_all(self):
                    for hive in self.hives.values():
                        for function in hive.zzz_bindbridgedrone.cleanup_functions:
                            function()

                    self.hives.clear()
                    self.handler_states.clear()
                    self.event_handlers.clear()

                stop_all = antenna("push", "trigger")
                trigger(stop_all, m_stop_all)

                # Pause all hives
                @modifier
                def m_pause_all(self):
                    # For every bound event handler, disable this
                    handler_states = self.handler_states
                    for bind_name in handler_states:
                        handler_states[bind_name] = False

                pause_all = antenna("push", "trigger")
                trigger(pause_all, m_pause_all)

                # Stop name
                stop = antenna("push", "id")
                v_stop = variable("id")
                connect(stop, v_stop)

                @modifier
                def m_stop(self):
                    stopped_name = self.v_stop

                    try:
                        hive = self.hives.pop(stopped_name)

                    except KeyError:
                        print("Couldn't find hive %s to stop" % stopped_name)

                    else:
                        for function in hive.zzz_bindbridgedrone.cleanup_functions:
                            function()

                    try:
                        del self.handler_states[stopped_name]
                        del self.event_handlers[stopped_name]
                    except KeyError:
                        print("Couldn't find hive %s to stop" % stopped_name)

                trigger(v_stop, m_stop)

                event = antenna("push", "event")
                v_event = variable("event")
                connect(event, v_event)

                @modifier
                def m_event(self):
                    """Push events into the bound hives"""
                    event = self.v_event
                    # They will handle if they are active or not
                    for event_func in self.eventfuncs:
                        event_func(event)

                trigger(v_event, m_event)

                def add_bound_handler(self, binder, bind_name, handler):
                    """Add a handler for the current bind name"""
                    if not bind_name in self.event_handlers:
                        self.event_handlers[bind_name] = {}
                        self.handler_states[bind_name] = True

                    self.event_handlers[bind_name][binder] = handler

                def place(self):
                    self.hives = {}
                    self.eventfuncs = []

                    self.handler_states = {}
                    self.event_handlers = {}

                    self.binder_instances = []
                    self.pre_binder_instances = []

                    for binder_instance in binders:
                        inst = binder_instance.getinstance()
                        if inst is not None:
                            self.binder_instances.append(inst)

                    for binder_instance in prebinders:
                        inst = binder_instance.getinstance()
                        if inst is not None:
                            self.pre_binder_instances.append(inst)

                    for binder_instance in self.binder_instances:
                        if getattr(self, binder_instance.parameter_name) != binder_instance.parameter_value:
                            continue

                        binder_instance.place()

                    for binder_instance in self.pre_binder_instances:
                        binder_instance.place()

                    libcontext.plugin("cleanupfunction",
                      libcontext.pluginclasses.plugin_single_required(self.m_stop_all))

            return bindhiveworker(*args, **kwargs)

        new_cls_dict["worker"] = staticmethod(lambda *args, **kwargs: get_bindhiveworker(*args, **kwargs))

        return type.__new__(metacls, name, (bind_baseclass,), new_cls_dict)


from .segments._helpersegment import reg_helpersegment

from . import myobject


class bind_baseclass(myobject):

    __metaclass__ = bindbuilder

    hive = None  #make some prebinders that change self.hive if you need dynamic binding
    worker = None


class reg_bindhelper(reg_helpersegment):

    def __new__(metacls, name, bases, dic, **kargs):
        return reg_helpersegment.__new__(metacls, name, bases, dic, **kargs)


class bindhelper(myobject):

    __metaclass__ = reg_bindhelper


class binderdrone(drone):
    def bind(self, binderworker, *antennavalues):
        pass

    def place(self):
        pass


class binderdronewrapper(binderdrone):
    def __init__(self, drone):
        self.drone = drone.getinstance()

    def bind(self, binderworker):
        self.drone.place()


class pluginbridge(binderdrone):
    """Place a socket for a plugin in the parent context, re-declaring it for the bound child context"""

    def __init__(self, pluginname, plugintype=libcontext.pluginclasses.plugin_supplier):
        self.pluginname = pluginname
        self.plugintype = plugintype

    def bind(self, binderworker):
        libcontext.plugin(self.pluginname, self.plugintype(self.plugin))

    def set_plugin(self, plugin):
        self.plugin = plugin

    def place(self):
        p = libcontext.socketclasses.socket_single_required(self.set_plugin)
        libcontext.socket(self.pluginname, p)


class binder(bindhelper):

    class binderinstance(object):

        def __init__(self, parameter_name, parameter_value, binder_drone_instance, antenna_names):
            self.parameter_name = parameter_name
            self.parameter_value = parameter_value
            self.binder_drone_instance = binder_drone_instance
            self.antenna_names = antenna_names

        def place(self):
            self.binder_drone_instance.place()
            #when placing the "bind" drone, call binderdrone.place()
            #when placing the new hive, call binderdrone.bind(bind object, ...) with the values of the specified antennanames

    def __init__(self, parameter_name, parameter_value, drone, antenna_names=None):
        if antenna_names is None:
            antenna_names = []

        if isinstance(antenna_names, str):
            antenna_names = [antenna_names]

        self.parameter_name = parameter_name
        self.parameter_value = parameter_value
        assert drone is None or issubclass(drone._wrapped_hive, binderdrone._wrapped_hive)
        self.drone = drone
        self.antenna_names = antenna_names

    def getinstance(self, __parent__=None):
        if self.drone is None:
            return

        binder_drone_instance = self.drone.getinstance(__parent__)
        return self.binderinstance(self.parameter_name, self.parameter_value, binder_drone_instance, self.antenna_names)


class prebinder(bindhelper):

    """ Called before the binding process begins, in order to modify bind antennas and have attributes"""

    class binderinstance(object):
        def __init__(self, binder_drone_instance, antennanames):
            self.binder_drone_instance = binder_drone_instance
            self.antennanames = antennanames

        def place(self):
            self.binder_drone_instance.place()
            #when placing the "bind" drone, call binderdrone.place()
            #before placing the new hive, call binderdrone.bind(bind object, ...) with the values of the specified antennanames

    def __init__(self, drone, antennanames=[]):
        if isinstance(antennanames, str): antennanames = [antennanames]
        assert drone is None or issubclass(drone._wrapped_hive, binderdrone._wrapped_hive)
        self.drone = drone
        self.antennanames = antennanames

    def getinstance(self, __parent__=None):
        if self.drone is None: return
        binder_drone_instance = self.drone.getinstance(__parent__)
        return self.binderinstance(binder_drone_instance, self.antennanames)


class bindparameter(bindhelper):  #bindhelper, just to know the order

    def __init__(self, value=None):
        self.value = value


class bindantenna(bindhelper):  #bindhelper, just to know the order

    def __init__(self, type):
        assert type in types, type
        self.type = type