import sys, os, spyder
from . import blendblockimporter


def file_exists(filename):
    # global os
    #if os is None: os = sys.modules["os"] #BGE re-initialization, or something...
    if os is None: return False
    filename2 = filename.replace(os.sep, "/")
    if blendblockimporter is not None:
        if _curr_blend_location is not None:
            filename3 = _curr_blend_location.lstrip("//") + "/" + filename2.lstrip("/")
            if filename3 in blendblockimporter.blendblockimporter.datablocks: return True
        if filename2 in blendblockimporter.blendblockimporter.datablocks: return True
        if filename2.lstrip("//") in blendblockimporter.blendblockimporter.datablocks: return True
    return os.path.exists(filename)


class readwrapper:
    def __init__(self, string):
        self._string = string

    def read(self):
        return self._string

    def close(self):
        pass


_curr_blend_location = None


def change_dir(directory):
    import os

    global _curr_blend_location
    directory2 = directory.replace(os.sep, "/")
    if _curr_blend_location is None:
        if directory2.startswith("//"):
            _curr_blend_location = directory2[2:].rstrip("/")
        else:
            os.chdir(directory)
    else:
        newdir = _curr_blend_location + "/" + directory2
        for k in blendblockimporter.blendblockimporter.datablocks.keys():
            if k.startswith(newdir):
                _curr_blend_location = newdir.rstrip("/")
        else:
            _curr_blend_location = None
            os.chdir(directory)


def file_load(filename, mode=None):
    import os

    if blendblockimporter is not None:
        ret = None
        f1 = filename.lstrip("//").replace(os.sep, "/")
        loc = _curr_blend_location
        f2 = None
        if loc is not None:
            f2 = loc + "/" + f1
        for f in f1, f2:
            if f is None: continue
            if f in blendblockimporter.blendblockimporter.datablocks:
                ret = blendblockimporter.blendblockimporter.datablocks[f]
                break
        if ret is not None: return readwrapper(ret)
    if mode is None:
        return open(filename)
    else:
        return open(filename, mode)


def file_access(filename, ok_mods):
    import os

    filename2 = filename.replace(os.sep, "/")
    supportedflags = os.F_OK + os.R_OK
    no_extraflags = (ok_mods & ~supportedflags) == 0
    if blendblockimporter is not None:
        if filename2 in blendblockimporter.blendblockimporter.datablocks: return no_extraflags
        if filename2.lstrip("//") in blendblockimporter.blendblockimporter.datablocks: return no_extraflags
    return os.access(filename, ok_mods)


done = False
for hook in sys.path_hooks:
    if hasattr(hook, "__name__") and hook.__name__ == "blendblockimporter":
        done = True
        break

if not done:
    sys.path_hooks.insert(0, blendblockimporter.blendblockimporter)
    sys.path_importer_cache.clear()
    if "//" not in sys.path: sys.path.append("//")
    spyder.loader._file_exists = file_exists
    spyder.loader._file_load = file_load
    spyder.loader._file_access = file_access
    spyder.loader._change_dir = change_dir
