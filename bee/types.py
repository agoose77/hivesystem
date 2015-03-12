from __future__ import print_function
import functools

_modes = ["push", "pull"]

_types = set((
    "event", "exception",
    "int", "float", "bool", "str",
    "mstr", "id",
    "object",
    "block", "blockcontrol", "blockmodel",
    "expression",
    "bee",
))

_objecttypes = "object", "mstr", "id", "block", "blockcontrol", "blockmodel", "expression", "bee"

_typemap = {
    "String": "str",
    "Material": "str",
    "Integer": "int",
    "Float": "float",
    "Bool": "bool",
    "FunctionLink": ("str", "function"),
    "ObjectLink": ("str", "object"),
    "ModuleLink": ("str", "module"),
    "Filename": ("str", "filename"),
}

from .event import event
from .mstr import mstr
from .reference import Reference

import spyder


def stringtupleparser(*tokens):
    if len(tokens) == 1:
        tokens = tokens[0]

    string_value = str(tokens).strip()
    if not string_value:
        return ""

    # String outer parenthesis
    if string_value[0] == "(" and string_value[-1] == ")":
        string_value = string_value[1:-1]

    parenthesis = 0
    quote = None
    tokens = []
    last = 0
    found = False
    skip = 0
    for index, character in enumerate(string_value):
        if character == "," and quote is None:
            if parenthesis == 0:
                tokens.append(string_value[last:index - skip])
                last = index + 1
                continue

        skip = 0
        if character == "(":
            parenthesis += 1
            found = True
            # if lnr == last: last += 1
        elif character == ")":
            parenthesis -= 1

        elif (character == "'" or character == '"') and not parenthesis:
            if quote is None and last == index:
                last += 1
                quote = character

            elif quote == character:
                quote = None
                skip = 1

        elif character == " " and quote is None and last == index:
            last += 1

    if parenthesis > 0:
        return string_value

    if last < len(string_value) - skip:
        # print("FINALTOK", value[last:len(value)-skip], last, skip)
        tokens.append(string_value[last:len(string_value) - skip])

    # print("TOKENS",v, tokens)
    if not found and len(tokens) == 1:
        return tokens[0]

    ret = []
    for token in tokens:
        ret.append(stringtupleparser(token))

    return tuple(ret)


eventparser = event


def boolparser(value):
    if value in (False, "False", 0, "0", ""):
        return False

    if value in (True, "True", 1, "1"):
        return True

    raise ValueError(value)


def spyderparser(spydertypename, value):
    import spyder, Spyder

    spyclass = getattr(Spyder, spydertypename)
    if not isinstance(value, str):
        return spyclass(value)

    try:
        typ, parsed = spyder.core.parse(value)
        if typ != spydertypename:
            raise TypeError

        return spyclass.fromdict(parsed)

    except:
        return spyclass(value)


def generic_constructor(type_=None):

    if type_ is None:
        def generic_constructor(v):
            from .beewrapper import beewrapper

            if isinstance(v, beewrapper):
                return v

            if isinstance(v, Reference):
                return v.obj

            try:
                return type(v)(v)

            except TypeError:
                return v

        return generic_constructor

    def generic_constructor(v):
        from .beewrapper import beewrapper

        if isinstance(v, beewrapper):
            return v

        if isinstance(v, Reference):
            return v.obj

        try:
            return type_(v)

        except TypeError:
            return v

    return generic_constructor


_parametertypes = {
    "bee": ("bee", generic_constructor()),
    "int": ("int", int),
    "float": ("float", float),
    "bool": ("bool", boolparser),
    "str": ("str", str),
    "mstr": ("mstr", generic_constructor(mstr)),
    "id": ("str", str),
    "object": ("str", generic_constructor()),
    "event": ("event", eventparser),
    "matrix": ("matrix", generic_constructor()),
    "expression": ("str", str),
}


def parse_parameters(unnamedparameters, namedparameters, args, kargs, exactmatch=True):
    kargs = dict(kargs)
    namedparameternames = [n[0] for n in namedparameters]
    for p in namedparameters[len(args):]:
        if p[0] not in kargs and p[2] != "no-defaultvalue": kargs[p[0]] = p[2]

    wrongargnr = False
    if exactmatch:
        if len(args) + len(kargs) != len(unnamedparameters) + len(namedparameters):
            wrongargnr = True
    else:
        if len(args) + len(kargs) < len(unnamedparameters) + len(namedparameters):
            wrongargnr = True
    if wrongargnr:
        raise TypeError("""
Number of required parameters: %d (keyword: %s)\n
Number of supplied parameters: %d (%d non-keyword, %d keyword)
""" % (len(unnamedparameters) + len(namedparameters), namedparameternames, len(args) + len(kargs), len(args),
       len(kargs)))
    if len(args) < len(unnamedparameters):
        raise TypeError("""
Number of required non-keyword parameters: %d\n
Number of supplied non-keyword parameters: %d (%d non-keyword, %d keyword)
""" % (len(unnamedparameters), len(args)))
    ret1 = []
    ret2 = {}
    for anr, a in enumerate(args):
        if anr == len(unnamedparameters): break
        pclass = unnamedparameters[anr][1]
        if pclass is object:
            pval = a
        elif a is None:
            pval = None
        else:
            pval = pclass(a)
        ret1.append(pval)
    args = args[len(unnamedparameters):]

    params = {}
    for p in enumerate(namedparameters): params[p[0]] = p[1]
    for anr, a in enumerate(args):
        if anr >= len(namedparameters):
            break
        pname, pclass, default = namedparameters[anr]
        pclass = pclass[1]
        if pclass is object:
            pval = a
        elif a is None:
            pval = None
        else:
            pval = pclass(a)
        ret2[pname] = pval

    unmatched = {}
    for pname in kargs:
        if pname in ret2:
            raise TypeError("Duplicate definition of parameter %s" % pname)
        ppar = [v[1] for v in namedparameters if v[0] == pname]
        if len(ppar) == 0:
            unmatched[pname] = kargs[pname]
            continue
        ppar = ppar[0]
        pclassname = ppar[0]
        pclass = ppar[1]
        a = kargs[pname]
        if pclassname == "bee":
            pval = a
            unmatched[pname] = a
        else:
            if pclass is object:
                pval = a
            elif a is None:
                pval = None
            else:
                pval = pclass(a)
        ret2[pname] = pval
    for pname, pclass, default in namedparameters:
        if pname not in ret2:
            raise TypeError("Undefined parameter '%s'" % pname)
    if exactmatch:
        return tuple(ret1), ret2
    else:
        return tuple(ret1), ret2, unmatched


def _parameterclass(parametertuple, *args, **kargs):
    return parse_parameters(parametertuple, [], args[0], kargs)[0]


def get_parameterclass(parclassname):
    t = typeclass(parclassname)
    if t.is_subtype:
        return get_parameterclass(parclassname[0])
    if isinstance(parclassname, tuple):
        parametertuple = [get_parameterclass(p) for p in parclassname]
        t0 = [t[0] for t in parametertuple]
        t1 = [t[1] for t in parametertuple]
        # return [t0, functools.partial(_parameterclass, t1), "no-defaultvalue"]
        #return [t0, functools.partial(_parameterclass, parametertuple), "no-defaultvalue"]
        return (tuple(t0), functools.partial(_parameterclass, parametertuple), "no-defaultvalue")
    elif parclassname in _typemap:
        return get_parameterclass(_typemap[parclassname])
    elif spyder.validvar2(parclassname):
        import Spyder

        return (parclassname, functools.partial(spyderparser, parclassname))
    else:
        return tuple(_parametertypes[parclassname]) + ("no-defaultvalue",)


def add_parameterclass(parclassname, parclassexpr, parclass):
    global _parametertypes
    assert not isinstance(parclassname, tuple)
    _parametertypes[parclassname] = (parclassexpr, parclass)


_pushtypes = set(("trigger", "toggle"))

_triggermodes = ["default", "input", "output", "update"]


class types_baseclass(object):
    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        v = self.value
        ov = other
        if isinstance(other, type(self)): ov = other.value
        if v in _typemap: v = _typemap[v]
        if ov in _typemap: ov = _typemap[ov]
        return v == ov


class modeclass(types_baseclass):
    def __init__(self, arg):
        if isinstance(arg, modeclass):
            self.value = arg.value
        else:
            if arg not in _modes:
                raise TypeError("Unknown channel mode '%s'" % arg)
            self.value = arg


class typeclass(types_baseclass):
    def __init__(self, arg):
        self.push_type = False
        self.is_subtype = False
        self.is_spyder = False
        self.is_compound = False
        if isinstance(arg, typeclass):
            self.value = arg.value
            self.is_subtype = arg.is_subtype
            self.is_compound = arg.is_compound
            self.push_type = arg.push_type
        elif isinstance(arg, tuple):
            try:
                for t in arg:
                    typeclass(t)
                self.is_compound = True
                self.value = arg
            except TypeError:
                typeclass(arg[0])
                self.is_compound = False
                self.is_subtype = True
                self.value = arg
                self.is_spyder = spyder.validvar2(arg[0])
        else:
            self.check_type(arg)
            self.is_compound = False
            self.value = arg
            self.is_spyder = spyder.validvar2(arg)

    def check_type(self, t):
        if spyder.validvar2(t): return
        if t not in _types:
            if t in _pushtypes:
                self.push_type = True
            else:
                raise TypeError("Unknown channel data type '%s'" % t)

    def get_tuple(self):
        if self.is_compound:
            return self.value
        else:
            return (self.value,)

    def __eq__(self, other):
        if isinstance(other, typeclass):
            for a1, a2 in (self, other), (other, self):
                if not a1.is_spyder: continue
                if not a2.is_subtype: continue
                if len(a2.value) < 2: continue
                if a2.value[:2] == ("object", "general"): return True
        else:
            while 1:
                if not self.is_spyder: break
                if not isinstance(other, tuple): break
                if len(other) < 2: break
                if other[:2] != ("object", "general"): break
                return True
        return types_baseclass.__eq__(self, other)


class mode_type(object):
    def __init__(self, mode, type=None):
        if isinstance(mode, mode_type):
            if type is not None: raise TypeError("Too many arguments")
            self.mode = mode.mode
            self.type = mode.type
        else:
            if type is None: raise TypeError("Too few arguments")
            self.mode = modeclass(mode)
            self.type = typeclass(type)
        if self.mode.value == "pull" and self.type.push_type:
            raise TypeError("Invalid channel data type %s for pull data" % self.type.value)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        other = mode_type(other)
        if self.mode != other.mode: return False
        if self.type != other.type: return False
        return True


class connection_inputclass(object):
    def __init__(self, arg):
        if isinstance(arg, str):
            self.value = arg
            self.bound = False
        else:
            self.test(arg)

    def test(self, arg):
        if hasattr(arg, "connection_input_type") and hasattr(arg, "connection_input"):
            self.value = arg
            self.bound = True
        else:
            raise TypeError("Segment %s cannot be used as output from another segment" % type(arg).__name__)

    def bind(self, classname, dic):
        if not self.bound:
            if self.value not in dic:
                raise KeyError("Segment name %s was not declared in worker class %s" % (self.value, classname))
            self.test(dic[self.value])


class connection_outputclass(object):
    def __init__(self, arg):
        if isinstance(arg, str):
            self.value = arg
            self.bound = False
        else:
            self.test(arg)

    def test(self, arg):
        if hasattr(arg, "connection_output_type") and hasattr(arg, "connection_output"):
            self.value = arg
            self.bound = True
        else:
            raise TypeError("Segment %s cannot be used as input to another segment" % type(arg).__name__)

    def bind(self, classname, dic):
        if not self.bound:
            if self.value not in dic:
                raise KeyError("Segment name %s was not declared in worker class %s" % (self.value, classname))
            self.test(dic[self.value])


class triggering_class(object):
    def __init__(self, arg, mode, pre):
        if mode not in _triggermodes:
            raise TypeError("Unknown trigger mode '%s'" % mode)
        self.mode = mode
        self.pre = pre
        if isinstance(arg, str):
            self.value = arg
            self.bound = False
        else:
            self.test(arg)

    def test(self, arg):
        if hasattr(arg, "triggering_" + self.mode):
            self.value = arg
            self.bound = True
        else:
            raise TypeError("Segment %s cannot send triggers in mode %s" % (type(arg).__name__, self.mode))

            # hack: change default pretrigger mode of variables from "input" to "output"
        from .segments.variable import variable

        if self.pre and isinstance(self.value, variable) and self.mode == "default":
            self.mode = "output"

    def bind(self, classname, dic):
        if not self.bound:
            if self.value not in dic:
                raise KeyError("Segment name %s was not declared in worker class %s" % (self.value, classname))
            self.test(dic[self.value])


class triggered_class(object):
    def __init__(self, arg, mode):
        if mode not in _triggermodes:
            raise TypeError("Unknown trigger mode '%s'" % mode)
        self.mode = mode
        if isinstance(arg, str):
            self.value = arg
            self.bound = False
        else:
            self.test(arg)

    def test(self, arg):
        if hasattr(arg, "triggered_" + self.mode):
            self.value = arg
            self.bound = True
        else:
            raise TypeError("Segment %s cannot receive triggers in mode %s" % (type(arg).__name__, self.mode))

    def bind(self, classname, dic):
        if not self.bound:
            if self.value not in dic:
                raise KeyError("Segment name %s was not declared in worker class %s" % (self.value, classname))
            self.test(dic[self.value])


class startvalueclass(object):
    def __init__(self, arg):
        if isinstance(arg, str):
            self.value = arg
            self.bound = False
        else:
            self.test(arg)

    def test(self, arg):
        if hasattr(arg, "set_startvalue"):
            self.value = arg
            self.bound = True
        else:
            raise TypeError("Segment %s cannot accept a start value" % type(arg).__name__)

    def bind(self, classname, dic):
        if not self.bound:
            if self.value not in dic:
                raise KeyError("Segment name %s was not declared in worker class %s" % (self.value, classname))
            self.test(dic[self.value])


def typecompare(t1, t2):
    try:
        tt1 = typeclass(t1)
        tt2 = typeclass(t2)
    except TypeError:
        return t1 == t2
    if not tt1.is_subtype and not tt2.is_subtype:
        return tt1 == tt2
    else:
        if not tt1.is_subtype: t1 = (t1,)
        if not tt2.is_subtype: t2 = (t2,)
        for v1, v2 in zip(t1, t2):
            if v1 != v2: return False
        return True
