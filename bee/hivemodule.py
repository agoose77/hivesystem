import functools
import libcontext
import sys, inspect
from .beewrapper import reg_beehelper, beehelper, beewrapper

from . import emptyclass, mytype, myobject

from . import _hivesubclass

reservedbeenames = ["getinstance", "build", "place", "close", "make_context", "init", "context"]
evbeenames = ["evin", "evout", "everr", "evexc"]

try:
    from weakref import WeakSet
except ImportError:
    from weakref import WeakKeyDictionary

    class WeakSet(WeakKeyDictionary):
        def add(self, key):
            self[key] = None
allreg = WeakSet()


class evcontextholder(myobject):
    def __init__(self, evclass, contextclass, evname):
        self.evclass = evclass
        self.contextclass = contextclass
        self.evname = evname
        self.ev = None

    def set_parent(self, parent):
        self.parent = parent
        self.ev = self.evclass(self.contextclass, self.evname, lambda: getattr(self.parent, "context"))

    def __getattr__(self, attr):
        return getattr(self.ev, attr)


class evwrapper(myobject):
    def __init__(self, evclass, contextclass, evname):
        self.evclass = evclass
        self.contextclass = contextclass
        self.evname = evname

    def getinstance(self, __parent__=None): return evcontextholder(self.evclass, self.contextclass, self.evname)

    def set_parameters(self, name, parameters): pass


from .configure import configure_base as configureclass
from .parameter import parameter as bee_parameter
from .attribute import attribute as bee_attribute


class hivewrapper(beewrapper):
    def hivecombine(self):
        try:
            if self._wrapped_hive.__hivecombined__ == True: return
        except AttributeError:
            pass
        b = self._wrapped_hive.beewrappers
        currcombobees = [v[0] for v in b if isinstance(v[0], str) and v[0].startswith("combobee")]
        combobeesnrs = [v[len("combobee"):] for v in currcombobees]
        m = max([0] + [int(v) for v in combobeesnrs if v.isdigit()])
        combobees = self._combobees
        for c in self._combobee_bases:
            combobees += c
        for beename, bee in combobees:
            for filt in self.__metaclass__.__registerfilters__:
                fbee = filt(bee)
                if fbee != None:
                    m += 1
                    b.append(("combobee" + str(m), fbee))
                    try:
                        allreg.add(fbee)
                    except TypeError:  # cannot weakref everything
                        pass
                    break
            else:
                raise TypeError("Combobee %s is of the wrong type: '%s'" % (beename, bee))
        self._wrapped_hive.__hivecombined__ = True


    def getinstance(self, __parent__=None):
        for name, bee in self._wrapped_hive.beewrappers:
            if isinstance(bee, configureclass): continue
            if not hasattr(bee, "combine"): continue
            if isinstance(bee.combine, tuple): continue
            bee.getinstance(__parent__)
            bee.combine()
        self.hivecombine()
        ret = beewrapper.getinstance(self, __parent__)
        if hasattr(self, "hmworkername") and \
                not isinstance(self.hmworkername, tuple):
            ret.hmworkername = self.hmworkername
        ret.set_parent(self)
        return ret


class hivecontext_base(libcontext.subcontext):
    __getting_attr__ = False

    def __getattr__(self, attr):
        if self.__getting_attr__: raise AttributeError
        self.__getting_attr__ = True
        try:
            ret = getattr(self._wrapping_hive, attr)
        except AttributeError:
            ret = (self, attr)
        self.__getting_attr__ = False
        return ret

    def build(self, hivename):
        pass

    def set_parent(self, parent):
        self.parent = parent

    def configure(self):
        pass

    def __place__(self):
        pass

    def __close__(self):
        pass


from . import types


class emptyhivecontext(hivecontext_base):
    beewrappers = []
    guiparams = {}
    parameters = []

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        __parent__ = kwargs.pop("__parent__", None)

        if __parent__ is not None:
            self.parent = __parent__

        try:
            param0, paramvalues, unmatched = types.parse_parameters([], self.parameters, args, kwargs, exactmatch=False)

        except TypeError as e:
            raise
            if self.parent is None or isinstance(self.parent, tuple):
                raise

            beename = self.parent._current
            args = tuple(beename) + e.args
            raise TypeError(*args)

        self.beeimports = unmatched
        self._paramvalues = paramvalues
        self._allparamvalues = dict(paramvalues)
        self._allparamvalues.update(unmatched)
        self.built = False
        self.bees = []
        self.buildmodifiers = []
        self.placemodifiers = []
        self.configured = False

        for bee_item in self.beewrappers:
            if not isinstance(bee_item, bee_attribute):
                continue

            bee_item[1].set_parent(self)

        for bee in self.beewrappers:
            if hasattr(bee, "combine") and not isinstance(bee.combine, tuple) and not isinstance(bee, configureclass):
                continue

            if isinstance(bee[1], bee_parameter): continue
            if isinstance(bee[1], bee_attribute):
                b = bee[1]

            else:
                assert hasattr(bee[1], "set_parameters") and not isinstance(bee[1].set_parameters, tuple), bee[1]
                bee[1].set_parameters(bee[0], self._paramvalues)
                self._current = bee[0]
                b = bee[1].getinstance(__parent__=self)
            self.bees.append((bee[0], b))

    def configure(self):
        self.beedict = dict(self.beeimports)
        self.beedict.update(dict(self.bees))
        for bee in self.bees:
            #posterior = isinstance(bee[1], hiveio)
            #if posterior: continue
            from .spyderhive.spyderhive import spyderconfigureplaceclass as scpc

            if isinstance(bee[1], configureclass) and not isinstance(bee[1], scpc): continue
            n = bee[1]
            if hasattr(n, "beeimports") and isinstance(n.beeimports, dict):
                for k in n.beeimports:
                    v = n.beeimports[k]
                    if isinstance(v, str) and v in self.beedict:
                        n.beeimports[k] = self.beedict[v]
                        #for bee in self.configurebees:
        for bee in self.bees:
            if not isinstance(bee[1], configureclass): continue
            n = bee[1]
            n.set_parameters(bee[0], self._allparamvalues)
            self._current = bee[0]
            n.configure(self.beedict)
        self.configured = True

    def build(self, hivename):

        for p in self.buildmodifiers: p(self)
        self.hivename = hivename
        self.beename = hivename
        libcontext.subcontext.__init__(self, hivename,
                                       hive=self._hive,
                                       import_parent_sockets=self._import_parent_sockets,
                                       import_parent_plugins=self._import_parent_plugins,
                                       import_parent_sockets_optional=self._import_parent_sockets_optional,
                                       import_parent_plugins_optional=self._import_parent_plugins_optional,
                                       import_parent_skip=self._import_parent_skip,
        )
        #self.configurebees = []

        #for bee in self.bees:
        #  n = bee[1]
        #  if hasattr(n, "configure") and not isinstance(n.configure, tuple):
        #    self.configurebees.append(bee)
        for bee in self.bees:
            #if bee in self.configurebees: continue
            from .spyderhive.spyderhive import spyderconfigureplaceclass as scpc

            if isinstance(bee[1], configureclass) and not isinstance(bee[1], scpc): continue
            n = bee[1]
            if hasattr(n, "make_context"):
                n.make_context()
            if hasattr(n, "set_parent"):
                if not isinstance(n.set_parent, tuple):
                    n.set_parent(self)
        for bee in self.bees:
            #if bee in self.configurebees: continue
            from .spyderhive.spyderhive import spyderconfigureplaceclass as scpc

            if isinstance(bee[1], configureclass) and not isinstance(bee[1], scpc): continue
            n = bee[1]
            if hasattr(n, "set_parent"):
                if not isinstance(n.set_parent, tuple):
                    n.set_parent(self)

        for bee in self.bees:
            try:
                from .spyderhive.spyderhive import spyderconfigureplaceclass as scpc

                if isinstance(bee[1], configureclass) and not isinstance(bee[1], scpc):
                    continue
                n = bee[1]
                if hasattr(n, "build"):
                    n.build(bee[0])
            except Exception as e:
                tb = sys.exc_info()[2]
                e.args = (self,) + tuple(bee) + e.args
                raise
        self.built = True

    def __place2__(self):
        pass

    def __place__(self):
        from . import io

        for p in self.placemodifiers:
            p(self)

        if not self.configured:
            self.configure()

        self.__place2__()

        for bee_name, bee in self.bees:

            if isinstance(bee, bee_attribute):
                continue

            is_helper = isinstance(bee, beehelper)
            is_io = isinstance(bee, io._io)

            if is_helper or is_io:
                if is_io:
                    bee[1].place0()

                continue

            if isinstance(bee, configureclass):
                continue

            bee.place()

            if isinstance(bee_name, str):
                if hasattr(bee, "bee") and not isinstance(bee.bee, tuple):
                    setattr(self, bee_name, bee.bee)

                else:
                    setattr(self, bee_name, bee)

        from .spyderhive.spyderhive import spyderconfigureplaceclass as scpc

        for bee_name, bee in self.bees:
            posterior1 = isinstance(bee, (beehelper, io.antenna_io, io.output_io))

            if isinstance(bee, configureclass) and not isinstance(bee, scpc):
                continue

            if not posterior1:
                continue

            bee.place()

        self.connect_contexts = []
        for bee_name, bee in self.bees:
            try:
                if hasattr(bee, "connect_contexts") and bee.connect_contexts != None and len(bee.connect_contexts) and \
                                bee.connect_contexts[-1] != "connect_contexts":
                    for context in bee.connect_contexts: self.connect_contexts.append(context)
            except TypeError:
                # TODO remove len(bee.connect_contexts)
                print("TYPEERROR")
                pass

    def __close__(self):
        for context in self.connect_contexts:
            context.close()

    @staticmethod
    def __get_beename__(self_or_class):
        from . import BuildError

        # Changed from "is not True"
        if not self_or_class.built:
            raise BuildError

        return self_or_class.beename

    def hive_init(self, bee_dict=None): # removed beedict parameter
        all_parameter_values = self._allparamvalues
        bee_dictionary = self.beedict

        for bee_name, bee in self.bees:
            if not isinstance(bee, configureclass):
                if not hasattr(bee, "_hivecontext"):
                    continue

                if isinstance(bee._hivecontext, tuple):
                    continue

            from .spyderhive.spyderhive import spyderconfigureplaceclass as scpc

            if isinstance(bee, configureclass) and not isinstance(bee, scpc):
                bee.set_parameters(bee_name, all_parameter_values)

            bee.hive_init(bee_dictionary)


class hivecontext(emptyhivecontext):
    def __place2__(self):
        from .worker import workerframe
        from .connect import connect

        mx = 0
        beelist = list(self.bees)

        for bee_name, bee in beelist:
            if isinstance(bee_name, int):
                mx = max(mx, bee_name)

        for bee_name, bee in beelist:
            if isinstance(bee_name, int):
                continue

            if (isinstance(bee, hivecontext_base) and bee._has_exc) or isinstance(bee, workerframe):
                c = connect((bee_name, "evexc"), "evexc").getinstance()
                self.bees.append((mx, c))
                mx += 1

        if self.hivename == "m":  # ##
            ppp = []
            for beename, bee in self.bees:
                if isinstance(bee, connect) and not isinstance(bee.target, tuple) and isinstance(bee.source, tuple) and \
                                bee.source[1] == "evexc":
                    name = bee.source[0]
                    if not isinstance(name, str):
                        name = name.beename

                    if name in ("b", "g", "k"):
                        ppp.append((beename, name, bee.target))


def get_reg_beehelper(fr, dicvalues):
    ret = []
    for value in dicvalues:
        try:
            allreg.add(value)

        except TypeError:  # cannot weakref everything
            pass

    if fr in reg_beehelper.reg:
        for a in reg_beehelper.reg[fr]:
            if hasattr(a, "place"):
                if a in allreg: continue
                allreg.add(a)
                ret.append(a)
        del reg_beehelper.reg[fr]
    return ret


def filter_reg_beehelper(arg):
    if hasattr(arg, "place"): return arg
    return None


def filter_evwrapper(arg):
    if isinstance(arg, evwrapper): return arg
    return None


def filter_isparameter(arg):
    if isinstance(arg, bee_parameter): return arg
    return None


def filter_isattribute(arg):
    if isinstance(arg, bee_attribute): return arg
    return None


unregister = None


class _hivebuilder(reg_beehelper):
    __registers__ = [get_reg_beehelper]
    __registerfilters__ = [filter_reg_beehelper, filter_evwrapper, filter_isparameter, filter_isattribute]
    __hivewrapper__ = hivewrapper

    def __init__(self, name, bases, dic, *args, **kargs):
        mytype.__init__(self, name, bases, dic)

    def __new__(metacls, name, bases, dic, specialmethods=[], **kargs):
        # print("HIVE-BUILD?", metacls, name)
        if "__metaclass__" in dic and dic["__metaclass__"] is not metacls:
            mc = dic["__metaclass__"]
            return mc.__new__(mc, name, bases, dic, specialmethods, **kargs)
        #print("HIVE-BUILD", metacls, name)
        from . import io

        hivebases = list(bases)
        bases0 = bases
        bases = []
        combobee_bases = []
        for base_cls in bases0:
            if hasattr(base_cls, "_wrapped_hive") and not isinstance(base_cls._wrapped_hive, tuple) and base_cls._wrapped_hive != None:
                bases.append(base_cls._wrapped_hive)
                bases += base_cls._wrapped_hive.__mro__[1:]
                combobee_bases += base_cls._combobee_bases
                combobee_bases.append(base_cls._combobees)
            else:
                bases.append(base_cls)
        bases = tuple(bases)

        rbases = list(bases)
        rbases.reverse()

        args = []
        hivedic = {}

        # More often than not, these tets value
        for base_cls in rbases:
            #
            if hasattr(base_cls, "__helpers__") and isinstance(base_cls.__helpers__, list):
                args += base_cls.__helpers__

        for base_cls in rbases:
            if hasattr(base_cls, "__hivedic__") and isinstance(base_cls.__hivedic__, dict):
                hivedic.update(base_cls.__hivedic__)

        #fix to preserve bee.attribute, even if overridden
        overriden_prefix = "overridden_attribute"
        overridden_attribute = [a[len(overriden_prefix):] for a in hivedic if a.startswith(overriden_prefix)]
        overridden_attribute = [a[1:] for a in overridden_attribute if a.startswith("_")]
        max_overridden = 0

        try:
            max_overridden = max((int(x) for x in overridden_attribute))

        except ValueError:
            pass

        for key, value in list(hivedic.items()):
            if key not in dic:
                continue

            if key == "_hivecontext" or key == "__module__":
                continue

            if not isinstance(value, bee_attribute):
                continue

            max_overridden += 1
            hivedic["%s_%d" % (overriden_prefix, max_overridden)] = value

        hivedic.update(dic)
        if "_hivecontext" not in dic and "_hivecontext" in hivedic:
            hivedic.pop("_hivecontext")

        dic = hivedic
        fr = inspect.currentframe()
        if len(specialmethods) == 0:  #KLUDGE: see pin/pin.py
            fr = fr.f_back

        else:
            fr = fr.f_back.f_back

        fr = id(fr)
        regargs = []
        for register in metacls.__registers__:
            newargs = register(fr, dic.values())
            if not newargs:
                newargs = []
            regargs += newargs

        unregisters = []
        for key in args + regargs + list(dic.values()):
            if unregister is None:
                continue
            if isinstance(key, unregister):
                unregisters.append(key.value)

        regargs = [a for a in regargs if not isinstance(a, unregister)]
        args += regargs

        if emptyclass in bases:
            dic["__helpers__"] = args
            bases = tuple([b for b in bases if b != emptyclass])
            return type.__new__(metacls, name, bases, dict(dic))

        bees = []
        for key, value in dic.items():
            assert key not in reservedbeenames, key

            if key == "_hivecontext":
                continue

            for filter_ in metacls.__registerfilters__:
                filtered_value = filter_(value)

                if filtered_value is not None:
                    bees.append((key, filtered_value))
                    break

        bees.sort(key=lambda entry: entry[0])
        minarg = max([0] + [bee[0] for bee in bees if isinstance(bee[0], int)])
        bees = bees + [(nr + minarg + 1, a) for nr, a in enumerate(args)]
        bees_ev = [n for n in bees if n[0] in evbeenames]
        bees_nev = [n for n in bees if n[0] not in evbeenames]
        bees = bees_nev + bees_ev
        bees = [b for b in bees if b[0] not in unregisters]

        guiparams = {"__beename__": name, "__ev__": []}
        for beename, bee in bees:
            if isinstance(bee, evwrapper):
                guiparams["__ev__"].append(bee.evname)

        parameters = []
        for beename, bee in bees:
            if isinstance(bee, bee_parameter):
                parameters.append((beename, bee.parameterclass, bee.gui_defaultvalue))
                v = None
                if bee.gui_defaultvalue != "no-defaultvalue":
                    v = bee.gui_defaultvalue

                if "parameters" not in guiparams:
                    guiparams["parameters"] = {}

                guiparams["parameters"][beename] = (bee.parameterclass, v)
                continue

            pnam = None
            if isinstance(bee, io.antenna):
                pnam = "antennas"
            elif isinstance(bee, io.output):
                pnam = "outputs"
            if pnam is not None:
                if pnam not in guiparams:
                    guiparams[pnam] = {}
                tar = bee.target[0]
                if isinstance(tar, str):
                    tar = [b[1] for b in bees if b[0] == tar][0]
                p = bee.guiparams
                guiparams[pnam][beename] = p
        rdic = {
            "__helpers__": args,
            "beewrappers": bees,
            "guiparams": guiparams,
            "parameters": parameters
        }
        globs = ["_has_exc", "_hive", "_import_parent_sockets", "_import_parent_plugins",
                 "_import_parent_sockets_optional", "_import_parent_plugins_optional", "_import_parent_skip"]
        for g in globs:
            if g in dic:
                rdic[g] = dic[g]
            else:
                for base_cls in bases:
                    if hasattr(base_cls, g):
                        rdic[g] = getattr(base_cls, g)
                        break
                else:
                    raise TypeError(g)
        for n in bees:
            if hasattr(n[1], "hiveguiparams"):
                if not hasattr(n[1], "configure") or isinstance(n[1].configure, tuple):
                    f = n[1].hiveguiparams
                    if hasattr(f, "__call__"): f(n[0], guiparams)

        if "_hivecontext" in dic:
            _hivecontext = dic["_hivecontext"]

        else:
            for base_cls in bases:
                if hasattr(base_cls, "_hivecontext"):
                    _hivecontext = getattr(base_cls, "_hivecontext")
                    break
                dic["_hivecontext"] = _hivecontext
            else:
                raise TypeError()

        hivecontextname = _hivecontext.__name__
        rdic["_hivecontext"] = _hivecontext
        rdic["__hivedic__"] = dict(dic)
        for spec in specialmethods:
            assert spec in dic, spec
            rdic[spec] = dic[spec]

        rhive = mytype(hivecontextname + ":" + name, (_hivecontext,), rdic)
        combobee_bases_unique = []
        for base_cls in combobee_bases:
            ok = True
            for bb in combobee_bases_unique:
                if base_cls is bb:
                    ok = False
                break
            if ok:
                combobee_bases_unique.append(base_cls)

        hivedict0 = {"_wrapped_hive": rhive, "guiparams": guiparams, "__metaclass__": metacls.__thisclass__,
                     "_combobees": [], "_combobee_bases": combobee_bases_unique, "__hivecombined__": False}
        beedictlist = [b for b in bees if isinstance(b[0], str)]
        beenames = [b[0] for b in beedictlist]
        from . import io

        beedictlist = [b for b in beedictlist if not isinstance(b[1], io.antenna) and not isinstance(b[1], io.output)]
        hivedict = dict(beedictlist)
        hivedict.update(hivedict0)

        for n in dic:  #non-bee attributes
            if n in unregisters:
                continue
            if n not in beenames and n not in hivedict: hivedict[n] = dic[n]

        for k in beenames:
            if k.startswith("@"):
                kk = k[1:]
                if kk in hivedict:
                    hivedict["$" + kk] = hivedict[kk]
                    del hivedict[kk]

        hivedict["__hivebases__"] = hivebases
        hivedict["__allhivebases__"] = bases
        ret = type.__new__(metacls, name, (metacls.__hivewrapper__,), hivedict)
        _hivesubclass[ret] = bases
        ret._wrapped_hive._wrapping_hive = ret
        return ret


_hivebuilder.__thisclass__ = _hivebuilder


class emptyclosedhive(emptyclass):
    __metaclass__ = _hivebuilder
    _hivecontext = emptyhivecontext
    _import_parent_sockets = []
    _import_parent_plugins = []
    _import_parent_sockets_optional = []
    _import_parent_plugins_optional = []
    _import_parent_skip = []
    _hive = True
    _has_exc = True


class emptyhive(emptyclosedhive, emptyclass):
    _import_parent_sockets_optional = [("bee", "init")]


from .eventhandler import eventhandler
from .drone import drone


class exceptionforwarder(drone):
    def __init__(self):
        self.targets = []

    def add_target(self, target):
        if target != self.read_exception:
            self.targets.append(target)

    def read_exception(self, exception):
        e = exception.grow_head(self.hivename)
        for tnr, t in enumerate(self.targets):
            # try:
            t(e)
            #except Exception:
            #if tnr == len(self.targets)-1: raise
            if e.cleared: break
        return e

    def set_parent(self, parent):
        self.hivename = parent.hivename

    def place(self):
        self.contextname = libcontext.get_curr_contextname()
        from libcontext.pluginclasses import plugin_supplier
        from libcontext.socketclasses import socket_container

        libcontext.socket(("evexc", "exception"), socket_container(self.add_target))
        libcontext.plugin(("evexc", "read-exception"), plugin_supplier(self.read_exception))


class evmixin(emptyhive):
    evin = evwrapper(libcontext.evsubcontext, libcontext.evincontext, "evin")
    evout = evwrapper(libcontext.evsubcontext, libcontext.evoutcontext, "evout")
    everr = evwrapper(libcontext.evsubcontext, libcontext.evoutcontext, "everr")
    evexc = evwrapper(libcontext.evsubcontext, libcontext.evexccontext, "evexc")


class hive(emptyhive, evmixin):
    _hivecontext = hivecontext
    eventhandler = eventhandler()
    exceptionforwarder = exceptionforwarder()


class closedhive(emptyclosedhive, evmixin):
    _hivecontext = hivecontext
    eventhandler = eventhandler()
    exceptionforwarder = exceptionforwarder()


class emptyframe(emptyclass):
    __metaclass__ = _hivebuilder
    _hivecontext = emptyhivecontext
    _import_parent_sockets = []
    _import_parent_plugins = []
    _import_parent_sockets_optional = []
    _import_parent_plugins_optional = []
    _import_parent_skip = ["evexc"]
    _hive = False
    _has_exc = True


class frame(emptyframe, evmixin):
    _hivecontext = hivecontext
    exceptionforwarder = exceptionforwarder()


class _initbee(object):
    def __init__(self):
        self.initfuncs = []

    def add_init(self, func):
        self.initfuncs.append(func)

    def init(self):
        for f in self.initfuncs: f()


class inithivecontext(hivecontext):
    def __init__(self, *args, **kargs):
        self._initbee = _initbee()
        hivecontext.__init__(self, *args, **kargs)

    def __place2__(self):
        socketclass = libcontext.socketclasses.socket_supplier
        libcontext.socket(("bee", "init"), socketclass(self._initbee.add_init))
        hivecontext.__place2__(self)

    def init(self):
        self._initbee.init()
        self.hive_init()


class inithive(closedhive):
    _hivecontext = inithivecontext


class apphivecontext(inithivecontext):
    app = None

    def __init__(self, *args, **kwargs):
        inithivecontext.__init__(self, *args, **kwargs)
        self.app = self.appbee.getinstance()

    def __getattr__(self, attr):
        try:
            if self.app is self: raise AttributeError
            return getattr(self.app, attr)
        except AttributeError:
            return inithivecontext.__getattr__(self, attr)

    def set_parent(self, parent):
        inithivecontext.set_parent(self, parent)
        self.app.parent = self

    def __place2__(self):
        self.app.place()
        inithivecontext.__place2__(self)

    def init(self):
        inithivecontext.init(self)
        try:
            i = self.app.init
        except AttributeError:
            pass
        else:
            if not isinstance(i, str) or isinstance(i, tuple): i()


def appcontext(appbee, *args, **kwargs):
    return mytype("appcontext", (apphivecontext,), {"appbee": appbee(*args, **kwargs)})


class unregister(beehelper):
    def __init__(self, value):
        self.value = value

    def getinstance(self, __parent__=None): return self

    def place(self): pass
