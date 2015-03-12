from .beewrapper import beewrapper, reg_beehelper

from . import emptyclass, Type


class dronebuilder(reg_beehelper):
    __droneclassname__ = "Drone"
    __reqdronefunc__ = "place"

    def __init__(self, name, bases, cls_dict, *args, **kargs):
        Type.__init__(self, name, bases, cls_dict)

    def __new__(metacls, name, bases, cls_dict, **kargs):
        if emptyclass in bases:
            bases = tuple([b for b in bases if b != emptyclass])
            return type.__new__(metacls, name, bases, dict(cls_dict))

        new_bases = []
        extra_bases = []

        for cls in bases:
            if hasattr(cls, "_wrapped_hive") and not isinstance(cls._wrapped_hive, tuple):
                new_bases.append(cls._wrapped_hive)
                extra_bases.append(cls._wrapped_hive)
                extra_bases += cls._wrapped_hive.__mro__[1:]

            else:
                new_bases.append(cls)
                extra_bases.append(cls)

        new_bases = tuple(new_bases)

        if metacls.__reqdronefunc__ not in cls_dict:

            for cls in extra_bases:
                if not hasattr(cls, metacls.__reqdronefunc__):
                    continue

                at = getattr(cls, metacls.__reqdronefunc__)
                if not isinstance(at, tuple):
                    break

            else:
                raise Exception("%s '%s' (or its base classes) must define a %s method" % (
                    metacls.__droneclassname__, name, metacls.__reqdronefunc__))

        if "__beename__" not in cls_dict:
            cls_dict["__beename__"] = name

        if "guiparams" not in cls_dict:
            inherited_guiparams = {}

            for cls in extra_bases:
                if hasattr(cls, "guiparams"):
                    inherited_guiparams.update(cls.guiparams)

            cls_dict["guiparams"] = inherited_guiparams

        cls_dict["guiparams"]["__beename__"] = cls_dict["__beename__"]

        edrone = type.__new__(metacls, name + "&", new_bases, dict(cls_dict))

        return type.__new__(metacls, name, (beewrapper,), {"_wrapped_hive": edrone, "guiparams": cls_dict["guiparams"],
                                                           "__metaclass__": dronebuilder})


class drone(emptyclass):
    __metaclass__ = dronebuilder


class combodronebuilder(dronebuilder):
    __droneclassname__ = "Combo drone"
    __reqdronefunc__ = "make_combo"


class combodrone(emptyclass):
    __metaclass__ = combodronebuilder


def combodronewrapper(*args, **kwargs):
    """Here be dragons"""

    for key in kwargs:
        if key not in ("combolist", "combodict"):
            raise TypeError("Unknown keyword argument '%s'" % key)

    combolist, combodict = None, None

    if "combolist" in kwargs:
        combolist = kwargs["combolist"]

    if "combodict" in kwargs:
        combodict = kwargs["combodict"]

    count = len(args) + (combolist is not None) + (combodict is not None)
    if count < 1:
        raise TypeError("Too few arguments for combodronewrapper")

    if count > 2:
        raise TypeError("Too many arguments for combodronewrapper")

    clist, cdict = [], {}
    exc1 = TypeError("Combolist must be list instance")
    exc2 = TypeError("Combodict must be dict instance")
    exc3 = TypeError("First argument must be list instance")
    exc4 = TypeError("First argument must be dict instance")
    exc5 = TypeError("First argument must be list or dict instance")
    exc6 = TypeError("Second argument must be list or dict instance")
    exc7 = TypeError("First and second arguments must be list and dict instances")

    if not args:
        if combolist is not None:
            if not isinstance(combolist, list):
                raise exc1

            clist = combolist

        if combodict is not None:
            if not isinstance(combodict, dict):
                raise exc2

            cdict = combodict

    elif len(args) == 1:
        if combolist is not None:
            if not isinstance(combolist, list):
                raise exc1

            clist = combolist

            if not isinstance(args[0], dict):
                raise exc4

            cdict = args[0]

        elif combodict is not None:
            if not isinstance(combodict, dict):
                raise exc2

            cdict = combodict
            if not isinstance(args[0], list):
                raise exc3

            clist = args[0]

        else:
            if not isinstance(args[0], (list, dict)):
                raise exc5

            elif isinstance(args[0], list):
                clist = args[0]

            else:
                cdict = args[0]

    else:  # len(args) == 2
        l1, d1 = isinstance(args[0], list), isinstance(args[0], dict)
        l2, d2 = isinstance(args[1], list), isinstance(args[1], dict)

        if not l1 and not d1:
            raise exc5

        if not l2 and not d2:
            raise exc6

        if l1 == l2:
            raise exc7

        if l1:
            clist = args[0]
        else:
            clist = args[1]

        if d1:
            cdict = args[0]
        else:
            cdict = args[1]

    class wrappedcombodrone(combodrone):
        def make_combo(self):
            return clist, cdict

    ret = wrappedcombodrone()

    from .hivemodule import allreg

    for item in clist + list(cdict.values()):
        if isinstance(item, list):
            it = item

        elif isinstance(item, dict):
            it = list(item.values())

        else:
            it = [item]

        for i in it:
            try:
                allreg.add(i)
            except TypeError:
                pass

    # Remove the combodrone from the current code frame and add it to the caller frame
    # as if it was initialized in the caller frame
    reg = ret.__metaclass__.reg
    import inspect

    fr = id(inspect.currentframe().f_back)
    fr2 = id(inspect.currentframe().f_back.f_back)
    if fr not in reg:
        reg[fr] = []

    if fr2 not in reg:
        reg[fr2] = []

    reg[fr].remove(ret)
    reg[fr2].append(ret)

    return ret


import libcontext


def dummydrone(plugindict=None, socketdict=None):

    class dummydrone(drone):

        def place(self):
            for name, plugin in self.plugindict.items():
                libcontext.plugin(name, plugin)

            for name, socket in self.socketdict.items():
                libcontext.socket(name, socket)

    if plugindict is None:
        plugindict = {}

    if socketdict is None:
        socketdict = {}

    ret = dummydrone()
    ret._wrapped_hive.plugindict = plugindict
    ret._wrapped_hive.socketdict = socketdict

    return ret
        
  

