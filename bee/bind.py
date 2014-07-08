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
    def __new__(cls, name, bases, dic):
        if name.endswith("bind_baseclass"):
            return mytype.__new__(cls, name, bases, dic)

        rdic = {"bindname": bindantenna("id")}
        rbases = list(bases)
        rbases.reverse()

        bindhelpers_nameless = []
        for b in bases:
            if hasattr(b, "__bindhelpers__"):
                for h in b.__bindhelpers__:
                    if h not in bindhelpers_nameless: bindhelpers_nameless.append(h)

        for b in rbases:
            rdic.update(b.__dict__)
        oldbindparameters = {}
        for k in rdic:
            if isinstance(rdic[k], bindparameter): oldbindparameters[k] = rdic[k]
        rdic.update(dic)

        fr = id(inspect.currentframe().f_back)
        bindhelpers_nameless += get_reg_bindhelper(fr, rdic.values())
        rdic["__bindhelpers__"] = bindhelpers_nameless
        bindhelpers = []
        rdkeys = rdic.keys()
        for k in sorted(rdkeys):
            a = rdic[k]
            if isinstance(a, bindhelper): bindhelpers.append((k, a))
        bindparameters = [h for h in bindhelpers if isinstance(h[1], bindparameter)]

        dicitems = [(k, dic[k]) for k in sorted(dic.keys())]
        morebindparameters = [(h[0], bindparameter(h[1])) for h in dicitems if
                              h not in bindparameters and h[0] in oldbindparameters]
        bindparameters += morebindparameters
        bindparameternames = set([h[0] for h in bindparameters])

        bindhelpers.sort(key=lambda n: n[0])

        bindantennas = [n for n in bindhelpers if isinstance(n[1], bindantenna)]
        bindantennatypes = tuple([b[1].type for b in bindantennas])
        for t in bindantennatypes:
            assert t in types, t
        if len(bindantennatypes) == 1: bindantennatypes = bindantennatypes[0]

        bindhelpers += [((nr + 1), a) for nr, a in enumerate(bindhelpers_nameless)]

        binders = [n[1] for n in bindhelpers if isinstance(n[1], binder)]
        for b in binders: assert b.parametername in bindparameternames, b.parametername

        prebinders = [n[1] for n in bindhelpers if isinstance(n[1], prebinder)]

        class bindbridge(drone):
            def __init__(self, bindobject):
                self.bindobject = bindobject

            def place(self):
                for binder in self.bindobject.binderinstances:
                    if getattr(self.bindobject, binder.parametername) != binder.parametervalue:
                        continue

                    values = {}
                    for antennaname in binder.antennanames:
                        values[antennaname] = self.bindobject.bindantennavalues[antennaname]
                    binder.binderdroneinstance.bind(self.bindobject, **values)
                s = libcontext.socketclasses.socket_supplier(lambda f: self.bindobject.startupfunctions.append(f))
                libcontext.socket("startupfunction", s)

        def get_bindhiveworker(*args, **kwargs):
            class bindhiveworker(bindworker):
                __beename__ = name + "-worker"
                bindworkerhive = rdic["hive"]

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

                #bindhive = None
                #if rdic["hive"] != None:
                #  class bindhive(rdic["hive"]): pass
                #prop = propclass(bindhive)
                #hive = property(prop.get, prop.set)
                #del bindhive, prop

                p = None
                for p in bindparameters:
                    locals()[p[0]] = p[1].value  #changes can only be made by subclassing
                del p

                bind = antenna("push", bindantennatypes)
                v_bind = variable(bindantennatypes)
                connect(bind, v_bind)

                @modifier
                def parse_bindantennas(self):
                    vb = self.v_bind
                    if len(bindantennas) == 1: vb = (vb,)
                    self.bindantennavalues = {}
                    for name, value in zip(bindantennas, vb):
                        self.bindantennavalues[name[0]] = value
                    """
                    for b in prebinders:
                      values = {}
                      for antennaname in b.antennanames:
                        values[antennaname] = self.bindantennavalues[antennaname]
                      b.prebinderfunc(self, **values)
                    """
                    for prebinder in self.prebinderinstances:
                        values = {}
                        for antennaname in prebinder.antennanames:
                            values[antennaname] = self.bindantennavalues[antennaname]
                        prebinder.binderdroneinstance.bind(self, **values)

                @modifier
                def do_bind(self):
                    if self.hive is None:
                        raise ValueError('"hive" is not defined in bind class "%s"' % name)

                    class newhive(self.hive):
                        zzz_bindbridgedrone = bindbridge(self)
                        raiser = raiser()
                        hiveconnect("evexc", raiser)

                    hive = newhive().getinstance()
                    try:
                        libcontext.push(self._context.contextname)
                        bindname = self.bindantennavalues["bindname"]
                        hive.build(bindname)
                        hive.place()
                    finally:
                        libcontext.pop()
                    hive.close()
                    hive.init()
                    for f in self.startupfunctions: f()
                    self.hives[bindname] = hive

                trigger(v_bind, parse_bindantennas)
                trigger(v_bind, do_bind)

                pause = antenna("push", "trigger")
                resume = antenna("push", "trigger")
                v_running = variable("bool")
                startvalue(v_running, True)

                @modifier
                def m_pause(self):
                    self.v_running = False

                trigger(pause, m_pause)

                @modifier
                def m_resume(self):
                    self.v_running = True

                trigger(resume, m_resume)

                stop = antenna("push", "id")
                v_stop = variable("id")
                connect(stop, v_stop)

                @modifier
                def m_stop(self):
                    del self.hives[self.v_stop]

                trigger(v_stop, m_stop)

                event = antenna("push", "event")
                v_event = variable("event")
                connect(event, v_event)

                @modifier
                def m_event(self):
                    if self.v_running:
                        for f in self.eventfuncs:
                            f(self.v_event)

                trigger(v_event, m_event)

                def place(self):
                    self.hives = {}
                    self.eventfuncs = []
                    self.binderinstances = []
                    self.prebinderinstances = []
                    self.startupfunctions = []
                    for b in binders:
                        inst = b.getinstance()
                        if inst != None: self.binderinstances.append(inst)
                    for b in prebinders:
                        inst = b.getinstance()
                        if inst != None: self.prebinderinstances.append(inst)

                    for b in self.binderinstances:
                        if getattr(self, b.parametername) != b.parametervalue: continue
                        b.place()
                    for b in self.prebinderinstances:
                        b.place()

            return bindhiveworker(*args, **kwargs)

        rdic["worker"] = staticmethod(lambda *args, **kwargs: get_bindhiveworker(*args, **kwargs))
        return type.__new__(cls, name, (bind_baseclass,), rdic)


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
        def __init__(self, parametername, parametervalue, binderdroneinstance, antennanames):
            self.parametername = parametername
            self.parametervalue = parametervalue
            self.binderdroneinstance = binderdroneinstance
            self.antennanames = antennanames

        def place(self):
            self.binderdroneinstance.place()
            #when placing the "bind" drone, call binderdrone.place()
            #when placing the new hive, call binderdrone.bind(bind object, ...) with the values of the specified antennanames

    def __init__(self, parametername, parametervalue, drone, antennanames=[]):
        if isinstance(antennanames, str): antennanames = [antennanames]
        self.parametername = parametername
        self.parametervalue = parametervalue
        assert drone is None or issubclass(drone._wrapped_hive, binderdrone._wrapped_hive)
        self.drone = drone
        self.antennanames = antennanames

    def getinstance(self, __parent__=None):
        if self.drone is None: return
        binderdroneinstance = self.drone.getinstance(__parent__)
        return self.binderinstance(self.parametername, self.parametervalue, binderdroneinstance, self.antennanames)


"""
class prebinder(bindhelper):
  def __init__(self,  prebinderfunc, antennanames=[]):
    if isinstance(antennanames, str): antennanames = [antennanames]  
    self.prebinderfunc = prebinderfunc
    self.antennanames = antennanames
    #signature: prebinderfunc(bind object, ...)
    #this function is called before the binding process begins, so that parameters and the hive attribute can be changed
"""


class prebinder(bindhelper):
    class binderinstance(object):
        def __init__(self, binderdroneinstance, antennanames):
            self.binderdroneinstance = binderdroneinstance
            self.antennanames = antennanames

        def place(self):
            self.binderdroneinstance.place()
            #when placing the "bind" drone, call binderdrone.place()
            #before placing the new hive, call binderdrone.bind(bind object, ...) with the values of the specified antennanames

    def __init__(self, drone, antennanames=[]):
        if isinstance(antennanames, str): antennanames = [antennanames]
        assert drone is None or issubclass(drone._wrapped_hive, binderdrone._wrapped_hive)
        self.drone = drone
        self.antennanames = antennanames

    def getinstance(self, __parent__=None):
        if self.drone is None: return
        binderdroneinstance = self.drone.getinstance(__parent__)
        return self.binderinstance(binderdroneinstance, self.antennanames)


class bindparameter(bindhelper):  #bindhelper, just to know the order
    def __init__(self, value=None):
        self.value = value


class bindantenna(bindhelper):  #bindhelper, just to know the order
    def __init__(self, type):
        assert type in types, type
        self.type = type
      
