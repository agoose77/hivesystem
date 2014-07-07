import glob as _glob
import os as _os


def find_imports(global_dict, local_dict, file_name):
    """Find available modules in a given import path

    :param global_dict: globals dictionary
    :param local_dict: locals dictionary
    :param file_name: path of __file__ calling helper
    """
    _pattern = _os.path.split(file_name)[0] + _os.sep + "*.py"
    _pyfiles = _glob.glob(_pattern);
    _pyfiles.sort()
    for _f in _pyfiles:
        _name = _os.path.split(_f)[1][:-3]
        if _name.startswith("_") or _name.startswith("~"):
            continue

        _temp = __import__(_name, global_dict, local_dict, [_name], 1)
        global_dict[_name] = getattr(_temp, _name)