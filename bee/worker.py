from __future__ import print_function
from .segments import reg_helpersegment, decoratorsegment
from .types import parse_parameters
from .beewrapper import beewrapper, reg_beehelper
import inspect
import libcontext
import functools

from . import emptyclass, mytype
from .event import exception
from .resolve import resolve


class workerframe(libcontext.subcontext):
    bee = None
    guiparams = {}
    __filtered_segmentnames__ = []

    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs
        self.built = False
        self._catch_targets = []
        self._ev = libcontext.evsubcontext(libcontext.evexccontext, "evexc", lambda: self.context)

    def build(self, beename):
        self.beename = beename
        args = [resolve(a) for a in self.args]
        kargs = {}
        for k in self.kargs:
            kargs[k] = resolve(self.kargs[k])
        try:
            self.bee = self.bee(self.beename, *args, **kargs)
            self.bee.parent = self.parent
        except TypeError as e:
            raise TypeError(self.beename, *e.args)
        libcontext.subcontext.__init__(self, beename, hive=False, import_parent_skip=["evexc"])
        self.built = True

    def add_catch_target(self, catch_target):
        self._catch_targets.append(catch_target)

    def catch(self, segmentname, exc_type, exc_value):
        e = exception((self.beename, segmentname), (exc_type, exc_value))
        for c in self._catch_targets:
            c(e)
            if e.cleared: break
        return e

    def __place__(self):
        from libcontext.socketclasses import socket_container

        libcontext.socket(("evexc", "exception"), socket_container(self.add_catch_target))
        self._ev.place()
        self.bee.evexc = self._ev.context
        self.bee.catchfunc = self.catch
        self.bee.__place__()

    def place(self):
        libcontext.subcontext.place(self)

    @staticmethod
    def __get_beename__(self_or_class):
        from . import BuildError

        if self_or_class.built is not True: raise BuildError
        return self_or_class.beename

    def __getattr__(self, attr):
        if attr == "set_parent":
            def set_parent(p):
                self.parent = p

            return set_parent
        return (self, attr)


class runtime_worker(object):
    _runtime_segment_classes = []
    parameters = []

    def __init__(self, beename, *args, **kargs):
        self._beename = beename
        self._runtime_segments = []
        self.__variabledict__ = {}
        self.catchfunc = None
        params = parse_parameters([], self.parameters, args, kargs)[1]
        for p in params:
            segment = [c for c in self._runtime_segment_classes if c.segmentname == p][0]
            segment.startvalue = params[p]
        for segmentclass in self._runtime_segment_classes:
            self._runtime_segments.append(segmentclass(self, beename))

    def place(self):
        pass

    def __place__(self):
        import libcontext

        self._context = libcontext.get_curr_context()
        self.place()
        for segment in self._runtime_segments:
            segment.place()
        if self.catchfunc != None:
            for segment in self._runtime_segments:
                segment.set_catchfunc(functools.partial(self.catchfunc, segment.segmentname))


class worker: pass  # placeholder; will be redefined later


class workerbuilder(reg_beehelper):
    __workerframeclass__ = workerframe
    __workerwrapperclass__ = beewrapper
    __runtime_workerclass__ = runtime_worker

    def __init__(self, name, bases, dic, *args, **kargs):
        mytype.__init__(self, name, bases, dic)

    def __new__(metacls, name, bases, dic, **kargs):
        forbidden = (
        "__init__", "__place__", "_runtime_segment_classes", "_beename", "_runtime_segments", "__variabledict__")
        for f in forbidden:
            if f in dic: raise AssertionError(f)
        if "__beename__" not in dic: dic["__beename__"] = name
        dic_guiparams = dic.get("guiparams", None)

        rworkerbases = []
        bases0 = bases
        bases = []
        for b in bases0:
            if hasattr(b, "_wrapped_hive") and not isinstance(b._wrapped_hive, tuple) and b._wrapped_hive != None:
                bases.append(b._wrapped_hive)
                rworkerbases.append(b._wrapped_hive.bee)
                bases += b._wrapped_hive.__mro__[1:]
            else:
                bases.append(b)
        bases = tuple(bases)

        ok = True
        basedic = {}
        for b in bases:
            if isinstance(b, worker) or hasattr(b, "__beedic__"):
                basedic.update(b.__beedic__)
                for n in b.__beedic__.values():
                    if hasattr(n, "__dict__"):
                        for attr in n.__dict__:
                            if attr.startswith("_connection"): ok = False

        basedic.update(dic)
        dic = basedic
        if emptyclass not in bases0:
            if not ok: raise TypeError(
                "Class definition of worker '%s': bee.worker with segments cannot be subclassed" % name)

        args = []
        fr = id(inspect.currentframe().f_back)
        if fr in reg_helpersegment.reg:
            args += [a for a in reg_helpersegment.reg[fr] if a not in dic.values()]
            del reg_helpersegment.reg[fr]

        if emptyclass in bases:
            dic["__helpers__"] = args
            bases = tuple([b for b in bases if b != emptyclass])
            return type.__new__(metacls, name, bases, dict(dic))

        segments = [(nr + 1, a) for nr, a in enumerate(args)] + list(dic.items())
        guiparams = {"__beename__": dic["__beename__"], "__ev__": ["evexc"]}
        if dic_guiparams: guiparams["guiparams"] = dic_guiparams
        parameters = []
        runtime_segment_classes = []
        moduledict = {"_runtime_segment_classes": runtime_segment_classes, "parameters": parameters}

        for segmentname, segment in segments:
            if segmentname in metacls.__workerframeclass__.__filtered_segmentnames__: continue
            if hasattr(segment, "bind") and hasattr(segment.bind, "__call__"):
                segment.bind(name, dic)
            if hasattr(segment, "connect") and hasattr(segment.connect, "__call__"):
                segment.connect(segmentname)
        for segmentname, segment in segments:
            if segmentname in metacls.__workerframeclass__.__filtered_segmentnames__: continue
            if hasattr(segment, "build") and hasattr(segment.build, "__call__"):
                runtime_segment_classes.append(segment.build(segmentname))
        for segmentname, segment in segments:
            processed = False
            if segmentname not in metacls.__workerframeclass__.__filtered_segmentnames__:
                if hasattr(segment, "connect"): processed = True
                if hasattr(segment, "build"):   processed = True
                if hasattr(segment, "guiparams") and hasattr(segment.guiparams, "__call__"):
                    segment.guiparams(segmentname, guiparams)
                    processed = True
                if hasattr(segment, "parameters") and hasattr(segment.parameters, "__call__"):
                    parameters.append(segment.parameters(segmentname))

            if (not processed and not isinstance(segmentname, int)):
                # "segment" is actually a method or property of the class...
                moduledict[segmentname] = segment
            elif isinstance(segment, decoratorsegment):
                moduledict[segmentname] = segment.decorated
        rnc = metacls.__runtime_workerclass__
        rworker = mytype("runtime_worker:" + name, tuple(rworkerbases) + (runtime_worker,), moduledict)
        nbc = metacls.__workerframeclass__
        rworkerframe = type(nbc.__name__ + ":" + name, (nbc,),
                            {"bee": rworker, "guiparams": guiparams, "__beedic__": dict(dic), "__helpers__": args})
        topdict = dict(moduledict)
        topdict.update({"_wrapped_hive": rworkerframe, "guiparams": guiparams})
        for f in forbidden:
            if f in topdict: del topdict[f]
        topdict["__metaclass__"] = workerbuilder
        ret = type.__new__(metacls, name + "&", (metacls.__workerwrapperclass__,), topdict)
        rworker.__workerclass__ = ret
        return ret


class worker(emptyclass):
    __metaclass__ = workerbuilder
 
