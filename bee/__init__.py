import spyder
from . import spy

spyder.load("models3d")
spyder.load("canvas")

from . import hivemap

_hivesubclass = {}

from .type import Type, Object
from .emptyclass import EmptyClass
from .worker import worker
from .drone import drone, combodrone, combodronewrapper

from .connect import connect
from .configure import Configure, ConfigureMultiple
from .init import init
from .io import Antenna, Output

from .hivemodule import frame, hive, closedhive, inithive, unregister
from .event import event

from .raiser import raiser
from .parameter import Parameter
from .parametergetter import ParameterGetter
from .attribute import attribute
from .resolve import resolve, resolvelist
from .reference import Reference

from .combohive import combohive


class BuildError(Exception): pass


def _get_all_hivebases(cls):
    if not hasattr(cls, "__hivebases__"): return [cls, ]
    ret = [cls, ]
    for c in cls.__hivebases__:
        r = _get_all_hivebases(c)
        for rr in r:
            if rr not in ret: ret.append(rr)
    return ret


def _get_all_subclasses(cls):
    if cls not in _hivesubclass: return [cls, ]
    ret = [cls, ]
    for c in _hivesubclass[cls]:
        ret += _get_all_subclasses(c)
    return ret


def hivesubclass(cls, cls2):
    if cls2._wrapped_hive._hivecontext in _get_all_subclasses(cls): return True
    if cls2 in _get_all_hivebases(cls): return True  # new
    return False


def hiveinstance(hive, hivecls):
    return hivesubclass(hive._wrapping_hive, hivecls)


from . import blendsupport
