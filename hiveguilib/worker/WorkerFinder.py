from __future__ import print_function, absolute_import

import sys
import os
import imp
import functools

import spyder
import Spyder

import bee


class FindWorkerState(object):
    def __init__(self):
        self.drones = {}
        self.hivemap_workers = {}
        self.metaworkers = {}
        self.spydermap_workers = {}
        self.spyderhives = {}
        self.suspect = []
        self.workers = {}

    def update(self, other):
        assert isinstance(other, FindWorkerState)
        self.workers.update(other.workers)
        self.metaworkers.update(other.metaworkers)
        self.hivemap_workers.update(other.hivemap_workers)
        self.spydermap_workers.update(other.spydermap_workers)
        self.drones.update(other.drones)
        self.spyderhives.update(other.spyderhives)
        self.suspect += other.suspect


def add_worker(worker, worker_name, find_worker_state, found_workers):
    try:
        if hasattr(worker, "guiparams") and ("antennas" in worker.guiparams or "outputs" in worker.guiparams):
            # worker, worker-like hive, or shim object (e.g. WorkerGUI segments)
            find_worker_state.workers[worker_name] = worker
            found_workers.add(id(worker))
            return True

        elif hasattr(worker, "metaguiparams"):
            find_worker_state.metaworkers[worker_name] = worker
            found_workers.add(id(worker))
            return True

        elif hasattr(worker, "__hivebases__"):
            if bee.frame in worker.__hivebases__ or bee.frame in worker.__allhivebases__:  # drone-like hive, treated as worker
                find_worker_state.workers[worker_name] = worker
                found_workers.add(id(worker))
                return True

            elif bee.spyderhive.spyderframe in worker.__hivebases__ \
                    or bee.spyderhive.spyderdicthive in worker.__hivebases__ \
                    or bee.spyderhive.spyderhivecontext in worker.__allhivebases__ \
                    or bee.spyderhive.spyderdicthivecontext in worker.__allhivebases__ \
                    or bee.combohive in worker.__hivebases__:  # spyderhive
                find_worker_state.spyderhives[worker_name] = worker
                found_workers.add(id(worker))
                return True

        elif hasattr(worker, "_wrapped_hive"):  # true drones
            if issubclass(worker._wrapped_hive, bee.drone):
                find_worker_state.drones[worker_name] = worker
                found_workers.add(id(worker))

        elif hasattr(worker, "__drone__"):  # drone-like shim object
            find_worker_state.drones[worker_name] = worker
            found_workers.add(id(worker))

    except TypeError:
        pass

    return False


def find_workers(mod, modname, done_mods, found_workers, star=False, search_path=True, lister=None, opener=None):
    if modname.endswith("__init__"):
        raise Exception

    if id(mod) in done_mods:
        return {}, {}

    if lister is None:
        lister = os.listdir
    if opener is None:
        opener = functools.partial(open, mode="r")
    find_worker_state = FindWorkerState()
    done_mods.add(id(mod))
    modname2 = modname.rstrip(".__init__")
    for v in dir(mod):
        if v in ("frame", "hive", "closedhive", "inithive", "raiser"):
            continue

        if isinstance(v, os.__class__):  # is a module...
            new_module_name = modname + "." + v
            new_find_worker_state = find_workers(v, new_module_name, done_mods, found_workers, lister=lister,
                                                 opener=opener)
            find_worker_state.update(new_find_worker_state)
            continue
        vv = getattr(mod, v)
        if id(vv) in found_workers: continue
        worker_name = modname + "." + v
        if hasattr(vv, "__module__") and vv.__module__ is not None:
            if not vv.__module__.startswith(modname2):
                if hasattr(vv, "guiparams") or hasattr(vv, "metaguiparams"):
                    if not vv.__module__.startswith("bee.segments"):
                        find_worker_state.suspect.append((worker_name, v, vv))
                continue
        add_worker(vv, worker_name, find_worker_state, found_workers)

    p = mod.__file__
    motif = ""
    if p.startswith("//"):
        p = p[2:]
        motif = "//"
    path = motif + os.path.split(p)[0]
    newmodules = []
    newstarmodules = []
    if search_path:
        for f in lister(path):
            ff = path + os.sep + f
            if (ff.endswith(".web") or ff.endswith(".hivemap") or ff.endswith(".spydermap")):
                try:
                    spydertype, spyderdata = spyder.core.parse(opener(ff).read())
                except:
                    import traceback

                    traceback.print_exc()
                    continue
                if ff.endswith(".web") or ff.endswith(".hivemap"):
                    if spydertype == "Hivemap":
                        try:
                            hivemap = Spyder.Hivemap(spyderdata)
                        except:
                            print("Error in importing '%s':" % ff)
                            import traceback

                            traceback.print_exc()
                            continue
                        newhivemapname = modname + ":" + f
                        find_worker_state.hivemap_workers[newhivemapname] = hivemap
                if ff.endswith(".web") or ff.endswith(".spydermap"):
                    if spydertype == "Spydermap":
                        try:
                            # spydermap = Spyder.Spydermap(spyderdata)
                            spydermap = Spyder.Spydermap.fromfile(ff)
                        except:
                            print("Error in importing '%s':" % ff)
                            import traceback

                            traceback.print_exc()
                            continue
                        newspydermapname = modname + "#" + f
                        find_worker_state.spydermap_workers[newspydermapname] = spydermap

            elif star:
                if ff.endswith(".py"):
                    n = f[:-len(".py")]
                    newstarmodules.append((n, ff))
                elif ff.endswith(".spy"):
                    # n = f[:-len(".spy")]
                    # newstarmodules.append((n,ff))
                    pass  #importing like this is not a good idea...
            else:
                if os.path.isdir(ff) and os.path.exists(ff + os.sep + "__init__.py"): newmodules.append(f)
    for n in newmodules:
        new_module_name = modname + "." + n
        if new_module_name in find_worker_state.workers or \
                        new_module_name in find_worker_state.metaworkers: continue

        try:
            if new_module_name not in sys.modules:
                __import__(new_module_name)
        except ImportError:
            print("Error in importing", new_module_name)
            import traceback

            traceback.print_exc()
            continue
        newmod = sys.modules[new_module_name]
        search_path = newmod.__file__.endswith("__init__.pyc") or mod.__file__.endswith("__init__.py")
        new_find_worker_state = \
            find_workers(newmod, new_module_name, done_mods, found_workers,
                         search_path=search_path,
                         lister=lister, opener=opener
            )
        find_worker_state.update(new_find_worker_state)
    for n, ff in newstarmodules:
        if n == "__init__": continue
        new_module_name = modname + "." + n
        if new_module_name in find_worker_state.workers or \
                        new_module_name in find_worker_state.metaworkers: continue
        try:
            if new_module_name not in sys.modules:
                if ff.endswith(".spy"):
                    # __import__(new_module_name)
                    raise Exception  # #importing like this is not a good idea...
                elif opener is not None:
                    __import__(new_module_name)
                    sys.modules[new_module_name].__file__ = ff
                else:
                    fil = open(ff, "r")
                    imp.load_module(new_module_name, fil, ff, ("py", "r", imp.PY_SOURCE ))
        except ImportError:
            print("Error in importing", new_module_name)
            import traceback

            traceback.print_exc()
            continue
        newmod = sys.modules[new_module_name]
        search_path = newmod.__file__.endswith("__init__.pyc") or mod.__file__.endswith("__init__.py")
        new_find_worker_state = \
            find_workers(
                newmod, new_module_name, done_mods, found_workers,
                search_path=search_path,
                lister=lister,
                opener=opener,
            )
        find_worker_state.update(new_find_worker_state)

    return find_worker_state


class WorkerFinder(object):
    @staticmethod
    def find_locationmodules(locationconfs, localdir=None, readlines=None):
        locationmodules = []

        syspath = []
        if localdir is not None: syspath = [localdir]
        syspath += list(sys.path)

        for lconf in locationconfs:
            if readlines is None:
                lines = open(lconf).readlines()
            else:
                lines = readlines(lconf)
            for l in lines:
                l = l.strip()
                if l.startswith("#"): continue
                if not len(l): continue
                if l.startswith("@"):
                    l = os.path.expandvars(l[1:])
                    if localdir is not None:
                        ll = localdir + os.sep + l
                        if os.path.isdir(ll):
                            syspath.append(ll)
                        else:
                            syspath.append(l)
                    else:
                        syspath.append(l)
                else:
                    locationmodules.append(l)
        return locationmodules, syspath

    def __init__(self, locationmodules, syspath, found_workers=None, lister=None, opener=None):
        self.lister = lister
        self.opener = opener
        self._done_mods = set()
        self._found_workers = set()
        if found_workers is not None:
            for w in found_workers:
                self._found_workers.add(w)

        find_worker_state = FindWorkerState()
        syspath_backup = list(sys.path)
        sys.path = syspath
        for m in locationmodules:
            star = False
            if m.endswith(".*"):
                star = True
                m = m[:-2]
            try:
                if m not in sys.modules:
                    __import__(m)
                mod = sys.modules[m]
                if mod.__file__.endswith(".spy"): continue
                search_path = mod.__file__.endswith("__init__.pyc") or mod.__file__.endswith("__init__.py")
                newfindworkerstate = \
                    find_workers(
                        mod, m, self._done_mods, self._found_workers, star,
                        search_path=search_path,
                        lister=self.lister,
                        opener=self.opener,
                    )
                find_worker_state.update(newfindworkerstate)
            except:
                print("Error in importing", m)
                import traceback

                traceback.print_exc()

        sys.path = syspath_backup

        for workername, varname, worker in find_worker_state.suspect:
            if id(worker) in self._found_workers: continue
            altworkername = worker.__module__ + "." + varname
            if altworkername in find_worker_state.workers or \
                            altworkername in find_worker_state.metaworkers:
                continue
            add_worker(
                worker, workername, find_worker_state, self._found_workers
            )

        self.workers = find_worker_state.workers
        self.metaworkers = find_worker_state.metaworkers
        self.hivemapworkers = find_worker_state.hivemap_workers
        self.spydermapworkers = find_worker_state.spydermap_workers
        self.drones = find_worker_state.drones
        self.spyderhives = find_worker_state.spyderhives
        self.typelist = set()
        for w in self.workers.values():
            gp = w.guiparams
            wtypes = list(gp.get("antennas", {}).values()) + \
                     list(gp.get("outputs", {}).values())
            for t in wtypes:
                self.typelist.add(t[1])                        
            