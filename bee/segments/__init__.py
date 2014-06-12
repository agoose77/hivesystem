class PullInputError(TypeError): pass


import glob as _glob, os as _os
from ._helpersegment import helpersegment, reg_helpersegment
from ._decoratorsegment import decoratorsegment
from .trigger import trigger
from .startvalue import startvalue

_pattern = _os.path.split(__file__)[0] + _os.sep + "*.py"
_pyfiles = _glob.glob(_pattern);
_pyfiles.sort()
for _f in _pyfiles:
    _name = _os.path.split(_f)[1][:-3]
    if _name.startswith("_"): continue
    _temp = __import__(_name, globals(), locals(), [_name], 1)
    globals()[_name] = getattr(_temp, _name)
