import libcontext
import spyder, Spyder

from .spyderhive import SpyderMethod, SpyderConverter, spyderframe

from ..types import stringtupleparser, boolparser, spyderparser
from .. import antenna, output, \
    parameter as _bee_parameter, get_parameter as _bee_get_parameter, \
    attribute as _bee_attribute
import os


def build_spydermap(sm, *args, **kwargs):
    sh = sm.spyderhive
    if len(sh) == 0:
        raise TypeError("Cannot build spydermaphive from Spydermap: No parent spyderhive defined")
    lastdot = sh.rindex(".")
    modname = sh[:lastdot]
    shname = sh[lastdot + 1:]
    shdict = {}
    shmod = __import__(modname, shdict, shdict, [shname])

    parenthive = getattr(shmod, shname)

    hivedata = dict(zip(sm.names, sm.objectdata))
    for wasp in sm.wasps:
        waspdata = spyderparser(wasp.spydertypename, wasp.spydervalue)
        target = hivedata[wasp.target]
        targetparam = getattr(target, wasp.targetparam)
        targetparam.append(waspdata)

    maphive = type("spydermaphive", (parenthive,), hivedata)
    return maphive


def make_spydermap(hm, __subcontext__=None, *args, **kwargs):
    maphive = build_spydermap(hm)
    try:
        return maphive(*args, **kwargs).getinstance()
    except TypeError as e:
        if __subcontext__ is None: raise
        raise TypeError(*((__subcontext__,) + e.args))


class spydermapframe(spyderframe):
    SpyderMethod("make_bee", "Spydermap", make_spydermap)
  
