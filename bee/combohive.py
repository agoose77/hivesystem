from .spyderhive import _spyderhive as spyderhive
from .hivemodule import *
from .configure import configure_base


class combohivewrapper(hivewrapper):
    def __init__(self, **beeimports):
        self.beeimports = beeimports
        self.args = []
        self.kargs = {}
        self.kargs2 = self.kargs.copy()
        self.instance = None
        for i in self.beeimports:
            im = self.beeimports[i]
            if not issubclass(im._wrapped_hive._hivecontext, hivecontext_base):
                raise TypeError("Combo hive can accept only hive injections, not %s=%s:%s" % (i, type(im), im))

    def hivecombine(self):
        pass

    def getinstance(self, __parent__=None):
        first = (self.instance is None)
        ret = hivewrapper.getinstance(self)
        if first:
            newbees = []
            for b in self.instance.beewrappers:
                ok = False
                if isinstance(b[0], str):
                    ok = True
                elif isinstance(b[1], spyderhive.spyderwrapper):
                    if isinstance(b[1].obj, spyderhive.spydermethod_or_converter): ok = True
                if ok: newbees.append(b)
            self._combobees += newbees
        self.instance.beewrappers = []
        self.instance.bees = []
        self.combined = False
        return ret

    def flatten(self, comboargs):
        if isinstance(comboargs, dict): return [], comboargs
        is_combolist = True
        for a in comboargs:
            try:
                assert not isinstance(a, dict)
                v1, v2 = a
                assert isinstance(v1, str)
            except Exception:
                is_combolist = False
                break
        ret = comboargs

        def dictupdate(d):
            for k in d:
                if k not in ret[1]: ret[1][k] = []
                v = d[k]
                if isinstance(v, list) or isinstance(v, tuple):
                    ret[1][k] += v
                else:
                    ret[1][k].append(v)

        if is_combolist:
            return ret, {}
        else:
            ret = [[], {}]
            for a in comboargs:
                if isinstance(a, list):
                    f = self.flatten(a)
                    ret[0] += f[0]
                    dictupdate(f[1])
                elif isinstance(a, dict):
                    dictupdate(a)
                elif isinstance(a, tuple):
                    ret[0] += a[0]
                    dictupdate(a[1])
            return ret[0], ret[1]

    def _combine_bee(self, bee):
        name, b = bee
        if isinstance(b, configure_base): return
        can_combo = False
        # if hasattr(b, "make_combo") and not isinstance(b.make_combo, tuple):
        try:
            comboargs = b.make_combo()
            if isinstance(comboargs, tuple):
                if len(comboargs) and isinstance(comboargs[0], str) and comboargs[0] == "make_combo":
                    raise AttributeError
            ok = False
            if isinstance(comboargs, list):
                comboargs = self.flatten(comboargs)
            if isinstance(comboargs, list):
                combolist, combodict = comboargs, {}
                ok = True
            elif isinstance(comboargs, dict):
                combolist, combodict = [], comboargs
                ok = True
            elif isinstance(comboargs, tuple):
                if len(comboargs) == 2:
                    if isinstance(comboargs[0], list) and isinstance(comboargs[1], dict):
                        combolist, combodict = comboargs
                        ok = True
            if ok == False:
                raise TypeError("Bee '%s' must return a combohive dict, list+dict or list" % name)
            for k in combodict:
                if k not in self.beeimports:
                    raise TypeError("Combohive dict key '%s' is not among injected hives" % k)
                v = combodict[k]
                h = self.beeimports[k]
                if not isinstance(v, list) and not isinstance(v, tuple):
                    h._combobees.append((None, v))
                else:
                    for vv in v:
                        if isinstance(vv, tuple):
                            h._combobees.append(vv)
                        else:
                            h._combobees.append((None, vv))
            if name is None: name = (None,)
            try:
                newname0 = tuple(name)
            except TypeError:
                newname0 = (name,)
            for vnr, v in enumerate(combolist):
                newname = newname0 + (vnr + 1,)
                try:
                    bee = v.getinstance()
                except (AttributeError, TypeError):
                    try:
                        ok = False
                        if hasattr(v, "typename") and isinstance(v.typename(), str):
                            ok = True
                            bee = v
                        if not ok: raise Exception
                    except Exception:
                        raise ValueError("Bee '%s' in combohive '%s' is not a combobee" % (newname, self))
                        newbee = (newname, bee)
                self._combine_bee(newbee)
            can_combo = True
        except AttributeError:
            raise
            pass
        if can_combo: return

        if isinstance(b, unregister):
            pass
        elif isinstance(b, hivecontext) and isinstance(name, int):
            pass
        else:
            if hasattr(b, "typename") and not isinstance(b.typename, tuple) and b.typename() == "Combobee":
                b.make_combo()
            else:
                raise ValueError("Bee '%s' in combohive '%s' is not a combobee" % (name, self))

    def _combine(self):
        self.combined = False
        beelist0 = self._combobees
        self._combobees = []
        beelist = []
        converters = []
        for bee0 in beelist0:
            b = bee0[1]
            try:
                bee = b.getinstance()
            except (AttributeError, TypeError):
                try:
                    ok = False
                    if hasattr(b, "typename") and isinstance(b.typename(), str):
                        ok = True
                        bee = b
                    if not ok: raise Exception
                except Exception:
                    raise ValueError("Bee '%s' in combohive '%s' is not a combobee" % (bee0[0], self))
            if isinstance(bee, spyderhive.spydermethod_or_converter):
                converters.append(bee)
            else:
                beelist.append((bee0[0], bee))
        for c in converters:
            c.func.enable()
        for bee in beelist:
            self._combine_bee(bee)
        for c in converters:
            c.func.disable()

    def combine(self):
        self._combine()


class _combohivebuilder(spyderhive._spyderhivebuilder):
    __hivewrapper__ = combohivewrapper


from .spyderhive.spyderhive import SpyderMethod


def spyder_make_combo(combobee):
    combolist, combodict = [], {}
    if combobee.combodict != None:
        for item in combobee.combodict:
            combodict[item.pname] = item.objects
    if combobee.combolist != None:
        combolist = [a for a in combobee.combolist]
    return combolist, combodict


class combohive(emptyhive, emptyclass):
    __metaclass__ = _combohivebuilder
    _has_exc = False
    SpyderMethod("make_combo", "Combobee", spyder_make_combo)
