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

    __filtered_segmentnames__ = []

    bee = None
    guiparams = {}

    def __init__(self, *args, **kargs):
        self.args = args
        self.kwargs = kargs
        self.built = False
        self._catch_targets = []
        self._ev = libcontext.evsubcontext(libcontext.evexccontext, "evexc", lambda: self.context)

    def build(self, beename):
        self.bee_name = beename
        args = [resolve(a) for a in self.args]
        kwargs = {}

        for key in self.kwargs:
            kwargs[key] = resolve(self.kwargs[key])

        try:
            self.bee = self.bee(self.bee_name, *args, **kwargs)
            self.bee.parent = self.parent

        except TypeError as e:
            raise TypeError(self.bee_name, *e.args)

        libcontext.subcontext.__init__(self, beename, hive=False, import_parent_skip=["evexc"])
        self.built = True

    def add_catch_target(self, catch_target):
        self._catch_targets.append(catch_target)

    def catch(self, segmentname, exc_type, exc_value):
        exc = exception((self.bee_name, segmentname), (exc_type, exc_value))
        for catch_targets in self._catch_targets:
            catch_targets(exc)
            if exc.cleared:
                break

        return exc

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

        if self.catchfunc is not None:
            for segment in self._runtime_segments:
                segment.set_catchfunc(functools.partial(self.catchfunc, segment.segmentname))


class worker: pass  # placeholder; will be redefined later


class workerbuilder(reg_beehelper):
    __workerframeclass__ = workerframe
    __workerwrapperclass__ = beewrapper
    __runtime_workerclass__ = runtime_worker

    def __init__(self, name, bases, dic, *args, **kwargs):
        mytype.__init__(self, name, bases, dic)

    def __new__(metacls, forbidden_name, bases, cls_dict, **kargs):
        forbidden = ("__init__", "__place__", "_runtime_segment_classes", "_beename", "_runtime_segments",
                     "__variabledict__")

        for forbidden_name in forbidden:
            if forbidden_name in cls_dict:
                raise AssertionError(forbidden_name)

        if "__beename__" not in cls_dict:
            cls_dict["__beename__"] = forbidden_name

        gui_parameters = cls_dict.get("guiparams", None)

        worker_bases = []
        listed_base_classes = bases
        bases = []

        for cls in listed_base_classes:
            if not (getattr(cls, "_wrapped_hive", None) is None or isinstance(cls._wrapped_hive, tuple)):
                bases.append(cls._wrapped_hive)
                worker_bases.append(cls._wrapped_hive.bee)
                bases += cls._wrapped_hive.__mro__[1:]

            else:
                bases.append(cls)

        bases = tuple(bases)
        inherited_cls_dict = {}
        contains_segments = False

        for cls in bases:
            if not(isinstance(cls, worker) or hasattr(cls, "__beedic__")):
                continue

            inherited_cls_dict.update(cls.__beedic__)
            for attribute in cls.__beedic__.values():
                if not hasattr(attribute, "__dict__"):
                    continue

                for attribute_name in attribute.__dict__:
                    if attribute_name.startswith("_connection"):
                        contains_segments = True
                        break

        inherited_cls_dict.update(cls_dict)
        cls_dict = inherited_cls_dict

        if emptyclass not in listed_base_classes and contains_segments:
            raise TypeError("Class definition of worker '%s': bee.worker with segments cannot be subclassed"
                            % forbidden_name)

        args = []
        caller_id = id(inspect.currentframe().f_back)
        if caller_id in reg_helpersegment.reg:
            args += [a for a in reg_helpersegment.reg[caller_id] if a not in cls_dict.values()]
            del reg_helpersegment.reg[caller_id]

        if emptyclass in bases:
            cls_dict["__helpers__"] = args
            bases = tuple([b for b in bases if b != emptyclass])
            return type.__new__(metacls, forbidden_name, bases, dict(cls_dict))

        segments = [(i + 1, a) for i, a in enumerate(args)] + list(cls_dict.items())
        guiparams = {"__beename__": cls_dict["__beename__"], "__ev__": ["evexc"]}
        if gui_parameters:
            guiparams["guiparams"] = gui_parameters

        parameters = []
        runtime_segment_classes = []
        moduledict = {"_runtime_segment_classes": runtime_segment_classes, "parameters": parameters}

        for segment_name, segment in segments:
            if segment_name in metacls.__workerframeclass__.__filtered_segmentnames__:
                continue

            if hasattr(segment, "bind") and hasattr(segment.bind, "__call__"):
                segment.bind(forbidden_name, cls_dict)

            if hasattr(segment, "connect") and hasattr(segment.connect, "__call__"):
                segment.connect(segment_name)

        for segment_name, segment in segments:
            if segment_name in metacls.__workerframeclass__.__filtered_segmentnames__:
                continue

            if hasattr(segment, "build") and hasattr(segment.build, "__call__"):
                runtime_segment_classes.append(segment.build(segment_name))

        for segment_name, segment in segments:
            processed = False

            if segment_name not in metacls.__workerframeclass__.__filtered_segmentnames__:
                if hasattr(segment, "connect"):
                    processed = True

                if hasattr(segment, "build"):
                    processed = True

                if hasattr(segment, "guiparams") and hasattr(segment.guiparams, "__call__"):
                    segment.guiparams(segment_name, guiparams)
                    processed = True

                if hasattr(segment, "parameters") and hasattr(segment.parameters, "__call__"):
                    parameters.append(segment.parameters(segment_name))

            if not processed and not isinstance(segment_name, int):
                # "segment" is actually a method or property of the class...
                moduledict[segment_name] = segment

            elif isinstance(segment, decoratorsegment):
                moduledict[segment_name] = segment.decorated

        rnc = metacls.__runtime_workerclass__
        rworker = mytype("runtime_worker:" + forbidden_name, tuple(worker_bases) + (runtime_worker,), moduledict)
        nbc = metacls.__workerframeclass__
        rworkerframe = type(nbc.__name__ + ":" + forbidden_name, (nbc,), {"bee": rworker, "guiparams": guiparams,
                                                                          "__beedic__": dict(cls_dict),
                                                                          "__helpers__": args})
        topdict = dict(moduledict)
        topdict.update({"_wrapped_hive": rworkerframe, "guiparams": guiparams})
        for forbidden_name in forbidden:
            if forbidden_name in topdict:
                del topdict[forbidden_name]

        topdict["__metaclass__"] = workerbuilder
        ret = type.__new__(metacls, forbidden_name + "&", (metacls.__workerwrapperclass__,), topdict)
        rworker.__workerclass__ = ret
        return ret


class worker(emptyclass):
    __metaclass__ = workerbuilder

