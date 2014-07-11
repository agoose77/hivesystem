from __future__ import print_function, absolute_import

import spyder
import Spyder

import copy
from bee.types import _parametertypes, _objecttypes, stringtupleparser
from functools import partial


def deslash(s):
    if isinstance(s, str): return s.replace("\\", "")
    return tuple([deslash(ss) for ss in s])


def stringtupleparser2(s):
    if s.count("'") % 2: return s
    if s.count('"') % 2: return s
    if isinstance(s, str):
        if s.startswith("(") and not s.rstrip().endswith(")"):
            s = s.replace("'", "")
            s = s[1:-2] + s[-1]
            return s
    ret = deslash(stringtupleparser(s))
    return ret


typemap = {
    "type": stringtupleparser2,
    "object": str,
    "pythoncode": str,
    "expression": str,
    "mstr": str,
}

parse_paramtypelist_error_index = None
parse_paramtypelist_error_type = None


def spyderparse(spyderclass, v):
    try:
        v2 = spyder.core.parse(v, mode="Spyder")
        if isinstance(v2, tuple) and len(v2) == 2 and isinstance(v2[0], str):
            v = v2[1]
    except:
        pass
    return spyderclass(v)


def parse_paramtypelist(paramtypelist, arglist):
    global parse_paramtypelist_error_index
    global parse_paramtypelist_error_type
    assert len(paramtypelist) == len(arglist)
    ret = []
    index = 0
    for p, arg in zip(paramtypelist, arglist):
        head, default = p
        if isinstance(head, str):
            typename, cons = head, None
        else:
            typename, cons = head[:2]
            if not callable(cons):
                typename, cons = head, None
        if cons is None and typename in typemap:
            cons = typemap[typename]
        v = default
        if arg is not None: v = arg
        vv = None
        if v is not None:
            if cons is not None:
                try:
                    vv = cons(v)
                except:
                    parse_paramtypelist_error_index = index
                    parse_paramtypelist_error_type = type
                    raise
            else:
                vv = v
        ret.append(vv)
        index += 1
    return ret


def typetuple(t):
    if not isinstance(t, tuple): return False
    if not len(t): return False
    for tt in t:
        if isinstance(tt, tuple):
            if not typetuple(tt): return False
            continue
        if not isinstance(tt, str): return False
        if tt not in _parametertypes and tt not in typemap: return False
    return True


def get_paramtypelist(workername, paramdic):
    """
    Interprets guiparams/metaguiparams into a list of parameter types
    Input possibilities:
      1. ((type, constructor, [str-defaultvalue]), defaultvalue)
      2. type (must be in paramdic, str or Spyder object if not) => ((type, paramdic[type]), None)
      2a. type as tuple
      3. (type, constructor) (constructor must be callable) => ((type, constructor), None)
      4. (type, defaultvalue) (type must be in paramdic, str if not; defaultvalue must not be callable) ((type, paramdic[type]), defaultvalue)
    Output: as 1.
    """
    ret = []
    paramnames = sorted(paramdic.keys())
    for parameter_name in list(paramnames):
        if not isinstance(parameter_name, str):
            continue

        if parameter_name.startswith("__"):
            continue

        ok = False
        parameter_object = paramdic[parameter_name]
        if isinstance(parameter_object, str):
            parameter_object = stringtupleparser2(parameter_object)

        desc = None
        if typetuple(parameter_object):  # WorkerGUI, variable segments
            print("Warning: Tuple variable segments do not have editable values: %s" % str(parameter_object))
            paramnames.remove(parameter_name)
            continue

        elif isinstance(parameter_object, tuple) and len(parameter_object) == 2:  # 1,3,4
            ppp = parameter_object[0]
            if isinstance(ppp, tuple) and len(ppp) in (2, 3):  #1
                if isinstance(ppp[0], str):
                    ok = True
                    desc = parameter_object
                elif isinstance(ppp[0], tuple):  #HiveGUI, parameter segments
                    print("Warning: Tuple parameter segments not supported: %s" % str(ppp[0]))

            elif isinstance(parameter_object[0], str):
                ok = True
                if callable(parameter_object[1]):  #3
                    desc = (parameter_object, None)

                else:  #4
                    head = (parameter_object[0], str)
                    if parameter_object[0] in _objecttypes:
                        head = ("object",) + parameter_object[1:]
                        parameter_object = (head, None)
                    elif parameter_object[0] in _parametertypes:
                        head = _parametertypes[parameter_object[0]]
                    elif spyder.validvar(parameter_object[0]):
                        cls = getattr(Spyder, parameter_object[0])
                        cons = partial(spyderparse, cls)
                        head = (parameter_object, cons)
                    elif parameter_object[0] in typemap:
                        pass
                    else:
                        ok = False
                    desc = (head, parameter_object[1])
        if not ok:
            if isinstance(parameter_object, tuple):  # 2a
                ok = True
                head = (parameter_object[0], str)
                if parameter_object[0] in _objecttypes:
                    head = ("object",) + parameter_object[1:]
                elif parameter_object[0] in _parametertypes:
                    head = _parametertypes[parameter_object[0]]
                elif spyder.validvar(parameter_object[0]):
                    cls = getattr(Spyder, parameter_object[0])
                    cons = partial(spyderparse, cls)
                    head = (parameter_object, cons)
                elif parameter_object[0] in typemap:
                    pass
                else:
                    ok = False
                desc = (head, None)
            elif isinstance(parameter_object, str):  # 2
                ok = True
                head = parameter_object
                if parameter_object in _objecttypes:
                    head = "object"
                elif parameter_object in _parametertypes:
                    head = _parametertypes[parameter_object]
                elif spyder.validvar2(parameter_object):
                    cls = getattr(Spyder, parameter_object)
                    cons = partial(spyderparse, cls)
                    head = (parameter_object, cons)
                elif parameter_object in typemap:
                    pass
                else:
                    ok = False
                desc = (head, None)
        if ok:
            ret.append(desc)
        if not ok:
            print("Warning: cannot interpret %s due to parameter '%s': '%s'" % (workername, parameter_name, parameter_object))
            return None, None
    return paramnames, ret


def get_param_pullantennas(antennas):
    pullantennas = []
    for a in antennas:
        if a == "inp":
            continue

        antenna = antennas[a]
        assert isinstance(antenna, tuple) and len(antenna) == 2, antenna
        if antenna[0] == "push":
            continue

        pp = antenna[1]
        if typetuple(pp):
            continue
        if pp == "any":
            continue
        pullantennas.append((a, pp))
    return pullantennas
