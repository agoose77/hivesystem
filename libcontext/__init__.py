from .context import context, subcontext, decode_context, encode_context, connect, clear as context_clear
from .plugin_base import plugin_base
from .socket_base import socket_base
from . import pluginclasses, socketclasses, pluginmixins, socketmixins
from .evcontext import evsubcontext, evincontext, evoutcontext, evexccontext

from . import tools

_contexts = {}  # TODO some kind of weakref system
_contextstack = []
_curr_context = None
_all_connections = set()


def clear():
    context_clear()
    _contexts.clear()
    _contextstack.clear()
    _all_connections.clear()
    global _curr_context
    _curr_context = None


def add_contextnames(context1, context2):
    c1 = context1
    if hasattr(c1, "decode") or hasattr(c1, "encode"):
        c1 = (c1,)
    c2 = context2
    if hasattr(c2, "decode") or hasattr(c2, "encode"):
        c2 = (c2,)
    if c1 == None: return c2
    if c2 == None: return c1
    return c1 + c2


def abscontextname(contexttuple):
    if _curr_context == None: return contexttuple
    if hasattr(contexttuple, "decode") or hasattr(contexttuple, "encode"):
        contexttuple = (contexttuple,)
    return _curr_context + contexttuple


def register_context(contextname, contextinstance):
    contextname = encode_context(contextname)
    if contextname in _contexts:
        _contexts[contextname].__overwritten__(contextinstance)
        contextinstance.__overwriting__(_contexts[contextname])
    _contexts[contextname] = contextinstance


def _push(contextname):
    global _curr_context
    contextname = encode_context(contextname)
    if contextname not in _contexts:
        raise Exception("Cannot enter context %s: context doesn't exist" % str(contextname))
    _contextstack.append(_curr_context)
    _curr_context = contextname
    return _contexts[contextname]


# ##

def push(contextname):
    return _push(abscontextname(decode_context(contextname)))


def pop():
    global _curr_context, _contextstack
    _curr_context = None
    if len(_contextstack):
        _curr_context = _contextstack[-1]
        _contextstack.pop()


def get_curr_contextname():
    return _curr_context


def get_curr_context():
    return _contexts[_curr_context]


def get_context(contextname):
    return _contexts[contextname]


def new_contextname(pattern):
    if abscontextname(pattern) not in _contexts: return pattern
    pattern = decode_context(pattern)
    try:
        xrange = xrange
    except NameError:
        xrange = range
    for n in xrange(1, 100000):
        ext = "-" + str(n)
        if isinstance(pattern, tuple):
            name = add_contextnames(pattern[:-1], pattern[-1] + ext)
        else:
            name = pattern + ext
        if abscontextname(name) not in _contexts: return name


def new_abscontextname(pattern):
    pattern = decode_context(pattern)
    if pattern not in _contexts: return pattern
    try:
        xrange = xrange
    except NameError:
        xrange = range

    for n in xrange(1, 100000):  #NOTE: should be range() in python3.x
        ext = "-" + str(n)
        name = add_contextnames(pattern[:-1], pattern[-1] + ext)
        if name not in _contexts: return name


def delete_context(contextname):
    c = encode_context(contextname)
    for k in list(_contexts.keys()):
        if len(k) < len(c):
            continue

        for n in range(len(c)):
            if k[n] != c[n]:
                break
        else:
            del _contexts[k]


def plugin(*args, **kargs):
    return _contexts[_curr_context].plugin(*args, **kargs)


def socket(*args, **kargs):
    return _contexts[_curr_context].socket(*args, **kargs)


def export_plugin(*args, **kargs):
    return _contexts[_curr_context].export_plugin(*args, **kargs)


def export_socket(*args, **kargs):
    return _contexts[_curr_context].export_socket(*args, **kargs)


def import_plugin(*args, **kargs):
    return _contexts[_curr_context].import_plugin(*args, **kargs)


def import_socket(*args, **kargs):
    return _contexts[_curr_context].import_socket(*args, **kargs)


def preclose(*args, **kargs):
    return _contexts[_curr_context].preclose(*args, **kargs)


def postclose(*args, **kargs):
    return _contexts[_curr_context].postclose(*args, **kargs)

  

