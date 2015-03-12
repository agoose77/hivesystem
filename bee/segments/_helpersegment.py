from __future__ import print_function
import inspect, functools

from .. import Type, Object


class reg_helpersegment(Type):
    reg = {}
    # def __init__(self, *args, **kargs):
    #   print("HELPERSUBNODE", name)
    __reg_enabled__ = True

    def __new__(cls, name, bases, dic):
        if name not in ("helpersegment", "hivehelper") and "__init__" in dic:
            dic["__init__old__"] = dic["__init__"]
            dic["__init__"] = reg_helpersegment.register(cls, dic["__init__"])
        ret = type.__new__(cls, name, bases, dic)
        return ret

    @staticmethod
    def register(cls, initfunc):
        def init(self, *args, **kargs):
            if cls.__reg_enabled__ and self.__class__.__reg_enabled__:
                fr = id(inspect.currentframe().f_back.f_back)
                if fr not in cls.reg: cls.reg[fr] = []
                cls.reg[fr].append(self)
            return self.__init__old__(*args, **kargs)

        return init


class helpersegment(Object):
    __metaclass__ = reg_helpersegment


