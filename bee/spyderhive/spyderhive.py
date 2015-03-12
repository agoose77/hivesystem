from ..hivemodule import *
from .. import hivemodule
from ..configure import configure_base

from .. import emptyclass, Type, Object


class spyderwrapper(Object):
    def __init__(self, obj):
        self.obj = obj
        self.combined = False

    def set_parameters(self, name, parameters):
        pass

    def getinstance(self, __parent__=None):
        return self.obj

    def __getattr__(self, attr):
        return getattr(self.obj, attr)


def filter_spyderreg(arg):
    if hasattr(arg, "typename") and hasattr(arg.typename, "__call__") and isinstance(arg.typename(),
                                                                                     str): return spyderwrapper(arg)
    return None


class spyderconfigureplaceclass(configure_base):
    def __init__(self, l1, l2):
        self.l1 = l1
        self.l2 = l2

    def configure(self, *arg):
        for i in self.l1:
            i.configure(*arg)

    def hive_init(self, *arg):
        for i in self.l1:
            i.hive_init(*arg)

    def place(self):
        for i in self.l2:
            i.place()

    def getinstance(self):
        return self


def spyderresultwrapper(l):
    class spyderconfigureclass(configure_base):
        def __init__(self, l):
            self.l = l

        def configure(self, *arg):
            for i in self.l:
                i.configure(*arg)

        def hive_init(self, *arg):
            for i in self.l:
                i.hive_init(*arg)

        def place(self):
            pass

    class spyderplaceclass(object):
        def __init__(self, l):
            self.l = l

        def place(self):
            for i in self.l:
                i.place()

        def getinstance(self): return self

    has_conf = True
    has_place = True
    ll = []
    ll1 = []
    ll2 = []
    for o in l:
        if isinstance(o, configure_base):
            no_conf0 = False
            no_place0 = True
        else:
            no_conf0 = not hasattr(o, "configure") or not hasattr(o.configure, "__call__") or not hasattr(o,
                                                                                                          "hive_init") or not hasattr(
                o.hive_init, "__call__")
            no_place0 = not hasattr(o, "place") or not hasattr(o.place, "__call__")
        if no_conf0 and no_place0:
            if not isinstance(o, list):
                raise TypeError("Spyderobject .make_bee() result has neither configure()/hive_init() nor place()")
            else:
                o = spyderresultwrapper(o)
                no_conf0 = not hasattr(o, "configure") or not hasattr(o.configure, "__call__") or not hasattr(o,
                                                                                                              "hive_init") or not hasattr(
                    o.hive_init, "__call__")
                no_place0 = not hasattr(o, "place") or not hasattr(o.place, "__call__")
                ll.append(o)
        else:
            ll.append(o)
            if no_conf0 == False: ll1.append(o)
            if no_place0 == False: ll2.append(o)
        if no_conf0: has_conf = False
        if no_place0: has_place = False
    if not has_conf and not has_place:
        # raise TypeError("Spyderobject .make_bee() results have neither all configure()/hive_init() nor all place()")
        return spyderconfigureplaceclass(ll1, ll2)
    if has_conf and has_place:
        # raise TypeError("Spyderobject .make_bee() results have all configure()/hive_init() and place()")
        return spyderconfigureplaceclass(ll, ll)
    if has_conf: return spyderconfigureclass(ll)
    if has_place: return spyderplaceclass(ll)

    raise Exception  # should never happen...


class reg_spydermethod_or_converter(Type):
    reg = {}

    def __new__(cls, name, bases, dic):
        if name not in ("spydermethod_or_converter",) and "__init__" in dic:
            dic["__init__old__"] = dic["__init__"]
            dic["__init__"] = reg_spydermethod_or_converter.register(dic["__init__"])
        return type.__new__(cls, name, bases, dic)

    @classmethod
    def register(cls, initfunc):
        def init(self, *args, **kargs):
            fr = id(inspect.currentframe().f_back.f_back)
            if fr not in cls.reg: cls.reg[fr] = []
            cls.reg[fr].append(self)
            return self.__init__old__(*args, **kargs)

        return init


class spydermethod_or_converter(Object):
    __metaclass__ = reg_spydermethod_or_converter


def get_spydermethod_or_converter_reg(fr, dicvalues):
    from ..hivemodule import allreg

    for d in dicvalues:
        try:
            allreg.add(d)
        except TypeError:  # cannot weakref everything
            pass
    ret = []
    if fr in reg_spydermethod_or_converter.reg:
        ret = [spyderwrapper(a) for a in reg_spydermethod_or_converter.reg[fr] if a not in dicvalues]
        del reg_spydermethod_or_converter.reg[fr]
    return ret


def filter_spydermethod_or_converter_reg(a):
    if isinstance(a, spydermethod_or_converter): return spyderwrapper(a)


from ..parameter import parameter as bee_parameter
from ..get_parameter import get_parameter as bee_get_parameter


def filter_parameter(a):
    if isinstance(a, bee_parameter): return a


class _spyderhivebuilder(hivemodule._hivebuilder):
    __registers__ = [get_spydermethod_or_converter_reg]
    __registerfilters__ = [
        filter_spyderreg, filter_reg_beehelper,
        filter_spydermethod_or_converter_reg, filter_evwrapper,
        filter_parameter
    ]


_spyderhivebuilder.__thisclass__ = _spyderhivebuilder


class spyderhivecontextmixin(Object):

    def __init__(self, *args, **kargs):
        self.buildmodifiers.append(self.process_spyderobjects)
        self.args = args
        self.kargs = kargs
        self._subcontextname = None

    def set_parent(self, parent):
        self.parent = parent

    def process_spyderobjects(self, arg):
        self.argbees = arg.bees
        spyder_indices = []
        converter_indices = []
        for onr, o in enumerate(arg.bees):
            obj = o[1]
            if hasattr(obj, "typename") and hasattr(obj.typename, "__call__") and isinstance(obj.typename(), str):
                spyder_indices.append(onr)
            if isinstance(obj, spydermethod_or_converter):
                converter_indices.append(onr)
        for onr in converter_indices:
            arg.bees[onr][1].func.init()
        for onr in spyder_indices:
            subcontext0, b = arg.bees[onr]
            pnam = []
            pc = self
            p = self.parent
            if p is not None: p = p.parent
            while p is not None and not isinstance(p, tuple):
                pnam.insert(0, p._contextname)
                if isinstance(p, spyderhivecontextmixin):
                    pnam = list(p._subcontextname) + [self.hmworkername] + pnam[1:]
                    break
                if p.parent is p: break
                pc = p
                p = p.parent
            self._subcontextname = tuple(pnam) + (subcontext0,)
            subcontext = self._subcontextname
            if len(self.args) or len(self.kargs):
                try:
                    r = b.make_bee(
                        *self.args, __subcontext__=subcontext, **self.kargs
                    )
                except TypeError as e:
                    if e.args[0] == subcontext: raise
                    try:
                        r = b.make_bee(__subcontext__=subcontext)
                    except TypeError as e:
                        if e.args[0] == subcontext: raise
                        r = b.make_bee()
            else:
                try:
                    r = b.make_bee(__subcontext__=subcontext)
                except TypeError as e:
                    if e.args[0] == subcontext: raise
                    r = b.make_bee()
            if hasattr(r, "place") and hasattr(r.place, "__call__"):
                pass
            elif hasattr(r, "configure") and hasattr(r.configure, "__call__"):
                pass
            elif hasattr(r, "hive_init") and hasattr(r.hive_init, "__call__"):
                pass
            elif isinstance(r, list):
                r = spyderresultwrapper(r)
            else:
                raise TypeError(
                    "Spyderobject.make_bee() => %s does not have a method place() nor configure() nor hive_init()\nSpyderobject:\n%s" % (
                    r, arg.bees[onr][1]))
            arg.bees[onr] = (arg.bees[onr][0], r)
        for onr in converter_indices:
            arg.bees[onr][1].func.disable()
        arg.bees = [o for onr, o in enumerate(arg.bees) if onr not in converter_indices]


class spyderhivecontext(spyderhivecontextmixin, hivecontext):
    def __init__(self, *args, **kargs):
        hivecontext.__init__(self, *args, **kargs)
        spyderhivecontextmixin.__init__(self, *args, **kargs)


class spyderinithivecontext(spyderhivecontextmixin, inithivecontext):
    def __init__(self, *args, **kargs):
        inithivecontext.__init__(self, *args, **kargs)
        spyderhivecontextmixin.__init__(self, *args, **kargs)


class spyderhive(closedhive, emptyclass):
    __metaclass__ = _spyderhivebuilder
    _hivecontext = spyderhivecontext


class spyderframe(frame, emptyclass):
    __metaclass__ = _spyderhivebuilder
    _hivecontext = spyderhivecontext


class spyderinithive(closedhive, emptyclass):
    __metaclass__ = _spyderhivebuilder
    _hivecontext = spyderinithivecontext


from .. import init as bee_init


class spyderdicthivecontextmixin(Object):
    def __init__(self, *args, **kargs):
        self.buildmodifiers.append(self.process_spyderobjects)
        self.args = args
        self.kargs = kargs
        self._subcontextname = None

    def set_parent(self, parent):
        self.parent = parent

    def process_spyderobjects(self, arg):
        self.argbees = arg.bees
        spyder_indices = []
        dictconfig = bee_init("dictionary_")
        for onr, o in enumerate(arg.bees):
            obj = o[1]
            if hasattr(obj, "typename") and hasattr(obj.typename, "__call__") and isinstance(obj.typename(), str):
                spyder_indices.append(onr)
        for onr in spyder_indices:
            objname, obj = arg.bees[onr]
            dictconfig[objname] = obj
        arg.bees = [o for onr, o in enumerate(arg.bees) if onr not in spyder_indices]
        arg.bees.append(("dictconfig", dictconfig))


class spyderdicthivecontext(spyderdicthivecontextmixin, hivecontext):
    def __init__(self, *args, **kargs):
        hivecontext.__init__(self, *args, **kargs)
        spyderdicthivecontextmixin.__init__(self, *args, **kargs)


class spyderdicthive0(frame, emptyclass):
    __metaclass__ = _spyderhivebuilder
    _hivecontext = spyderdicthivecontext


class spyderdicthive(spyderdicthive0):
    dictionary = bee_parameter("object")
    dictionary_ = bee_get_parameter("dictionary")


del spyderdicthive0


class SpyderConverter(spydermethod_or_converter):
    def __init__(self, intype, outtype, converterfunc):
        from .. import spy
        import spyder

        self.func = spyder.core.defineconverter(intype, outtype, converterfunc)
        self.func.disable()


class SpyderMethod(spydermethod_or_converter):
    def __init__(self, methodname, spydertype, methodfunc):
        from .. import spy
        import spyder

        self.func = spyder.core.definemethod(methodname, spydertype, methodfunc)
        self.func.disable()
  
