import libcontext
from .segments import *
from . import worker, drone
from .bindworker import bindworker
from . import connect as hiveconnect
import inspect

from .types import _types as types
from .raiser import raiser

from .bind import *
from .bindbridge import bindbridge
from . import myobject, mytype


def get_reg_bindhelper(fr, dicvalues):
    from .hivemodule import allreg

    for d in dicvalues:
        try:
            allreg.add(d)
        except TypeError:  # cannot weakref everything
            pass
    ret = []
    if fr in reg_bindhelper.reg:
        for a in reg_bindhelper.reg[fr]:
            if a in allreg: continue
            allreg.add(a)
            ret.append(a)
        del reg_bindhelper.reg[fr]
    return ret


class staticbindbuilder(bindbuilder):
    def __new__(cls, name, bases, dic):
        if name == "staticbind_baseclass":
            return mytype.__new__(cls, name, bases, dic)
        rdic = {}
        rbases = list(bases)
        rbases.reverse()

        bindhelpers_nameless = []
        for b in bases:
            if hasattr(b, "__bindhelpers__"):
                for h in b.__bindhelpers__:
                    if h not in bindhelpers_nameless: bindhelpers_nameless.append(h)

        for b in rbases:
            bdict = b.__dict__
            if issubclass(b, bind_baseclass):
                bdict = dict(bdict)
                bdict.pop("bindname", None)
            rdic.update(bdict)
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
        bindantennas = [n for n in bindantennas if n[0] != "bindname"]
        if len(bindantennas):
            raise TypeError("Static bind workers cannot take bindantennas: %s" % str(bindantennas))

        bindhelpers += [((nr + 1), a) for nr, a in enumerate(bindhelpers_nameless)]

        binders = [n[1] for n in bindhelpers if isinstance(n[1], binder)]
        for b in binders: assert b.parametername in bindparameternames, b.parametername

        prebinders = [n[1] for n in bindhelpers if isinstance(n[1], prebinder)]
        if len(prebinders): raise Exception("Prebinders not implemented for static bind bees")

        def get_bindhiveworker(*args, **kwargs):
            class bindhiveworker(bindworker):
                __beename__ = name + "-worker"
                bindworkerhive = rdic["hive"]
                bindname = antenna("pull", "id")
                b_bindname = buffer("pull", "id")
                trigger_bindname = triggerfunc(b_bindname)
                connect(bindname, b_bindname)

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

                # bindhive = None
                #if rdic["hive"] != None:
                #  class bindhive(rdic["hive"]): pass
                #prop = propclass(bindhive)
                #hive = property(prop.get, prop.set)
                #del bindhive, prop
                p = None
                for p in bindparameters:
                    locals()[p[0]] = p[1].value  #changes can only be made by subclassing
                del p

                def do_bind(self):
                    #if not hasattr(self, "hive") or self.hive is None:
                    #  print(self, self.__dict__)
                    #  raise ValueError('"hive" is not defined in bind class "%s"' % name)
                    class newhive(self.hive):
                        zzz_bindbridgedrone = bindbridge(self)
                        raiser = raiser()
                        hiveconnect("evexc", raiser)

                    hive = newhive().getinstance()
                    try:
                        libcontext.push(self._context.contextname)
                        hive.build(self.b_bindname)
                        hive.place()
                    finally:
                        libcontext.pop()
                    hive.close()
                    hive.init()
                    for f in self.startupfunctions: f()
                    self.hives[self.b_bindname] = hive

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
                            f(self, v_event)

                trigger(v_event, m_event)

                def init(self):
                    self.trigger_bindname()
                    self.do_bind()

                def place(self):
                    self.hives = {}
                    self.eventfuncs = []
                    self.binderinstances = []
                    self.startupfunctions = []
                    done = set()
                    for b in binders:
                        inst = b.getinstance()
                        if inst != None:
                            params = inst.parametername, inst.parametervalue, str(
                                inst.binderdroneinstance.__beename__), tuple(inst.antennanames)
                            if params in done: continue
                            done.add(params)
                            self.binderinstances.append(inst)
                    for b in self.binderinstances:
                        if getattr(self, b.parametername) != b.parametervalue: continue
                        b.place()
                    p = libcontext.pluginclasses.plugin_single_required(self.init)
                    libcontext.plugin("startupfunction", p)

            return bindhiveworker(*args, **kwargs)

        rdic["worker"] = staticmethod(lambda *args, **kwargs: get_bindhiveworker(*args, **kwargs))
        return type.__new__(cls, name, (staticbind_baseclass,), rdic)


from .segments._helpersegment import reg_helpersegment

import sys

python3 = (sys.version_info[0] == 3)
if python3:
    from .bind import bind_baseclass

    class staticbind_baseclass(bind_baseclass, myobject):
        __metaclass__ = staticbindbuilder
        hive = None  # make some prebinders that change self.hive if you need dynamic binding
        worker = None
else:
    class staticbind_baseclass(myobject):
        __metaclass__ = staticbindbuilder
        hive = None  # make some prebinders that change self.hive if you need dynamic binding
        worker = None

