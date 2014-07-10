from __future__ import print_function, absolute_import

import sys
import os
import imp
import functools
import traceback

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

    return False


def find_workers(module, module_name, done_mods, found_workers, star=False, search_path=True, lister=None, opener=None):
    if module_name.endswith("__init__"):
        raise Exception

    if id(module) in done_mods:
        return {}, {}

    if lister is None:
        lister = os.listdir

    if opener is None:
        opener = functools.partial(open, mode="r")

    find_worker_state = FindWorkerState()
    done_mods.add(id(module))

    for attribute_name in dir(module):
        if attribute_name in ("frame", "hive", "closedhive", "inithive", "raiser"):
            continue

        # If it is a module
        if isinstance(attribute_name, os.__class__):
            new_module_name = module_name + "." + attribute_name
            new_find_worker_state = find_workers(attribute_name, new_module_name, done_mods, found_workers,
                                                 lister=lister, opener=opener)
            find_worker_state.update(new_find_worker_state)
            continue

        attribute = getattr(module, attribute_name)
        if id(attribute) in found_workers:
            continue

        worker_name = module_name + "." + attribute_name
        if hasattr(attribute, "__module__") and attribute.__module__ is not None:
            if not attribute.__module__.startswith(module_name):
                if hasattr(attribute, "guiparams") or hasattr(attribute, "metaguiparams"):
                    if not attribute.__module__.startswith("bee.segments"):
                        find_worker_state.suspect.append((worker_name, attribute_name, attribute))
                continue
        add_worker(attribute, worker_name, find_worker_state, found_workers)

    module_path = module.__file__
    motif = ""
    if module_path.startswith("//"):
        module_path = module_path[2:]
        motif = "//"

    search_path = motif + os.path.split(module_path)[0]
    new_modules = []
    newstarmodules = []

    if search_path:
        for filename in lister(search_path):
            file_path = search_path + os.sep + filename
            if (file_path.endswith(".web") or file_path.endswith(".hivemap") or file_path.endswith(".spydermap")):
                try:
                    spydertype, spyderdata = spyder.core.parse(opener(file_path).read())

                except:
                    traceback.print_exc()
                    continue

                if file_path.endswith(".web") or file_path.endswith(".hivemap") or file_path.endswith(".spydermap"):
                    if spydertype == "Hivemap":
                        try:
                            hivemap = Spyder.Hivemap(spyderdata)

                        except:
                            print("Error in importing '%s':" % file_path)
                            traceback.print_exc()
                            continue

                        newhivemapname = module_name + ":" + filename
                        find_worker_state.hivemap_workers[newhivemapname] = hivemap

                    elif spydertype == "Spydermap":
                        try:
                            # spydermap = Spyder.Spydermap(spyderdata)
                            spydermap = Spyder.Spydermap.fromfile(file_path)

                        except:
                            print("Error in importing '%s':" % file_path)
                            traceback.print_exc()
                            continue

                        newspydermapname = module_name + "#" + filename
                        find_worker_state.spydermap_workers[newspydermapname] = spydermap

            elif star:
                if file_path.endswith(".py"):
                    name = filename[:-len(".py")]
                    newstarmodules.append((name, file_path))

                elif file_path.endswith(".spy"):
                    # importing like this is not a good idea...
                    # n = f[:-len(".spy")]
                    # newstarmodules.append((n,ff))
                    pass
            else:
                if os.path.isdir(file_path) and os.path.exists(file_path + os.sep + "__init__.py"):
                    new_modules.append(filename)

    for name in new_modules:
        new_module_name = module_name + "." + name
        if new_module_name in find_worker_state.workers or new_module_name in find_worker_state.metaworkers:
            continue

        try:
            if new_module_name not in sys.modules:
                __import__(new_module_name)

        except Exception:
            print("Error in importing", new_module_name)

            traceback.print_exc()
            continue

        new_module = sys.modules[new_module_name]

        search_path = new_module.__file__.endswith("__init__.pyc") or module.__file__.endswith("__init__.py")
        new_find_worker_state = find_workers(new_module, new_module_name, done_mods, found_workers,
                                             search_path=search_path,  lister=lister, opener=opener)
        find_worker_state.update(new_find_worker_state)

    for name, file_path in newstarmodules:
        if name == "__init__":
            continue

        new_module_name = module_name + "." + name
        if new_module_name in find_worker_state.workers or new_module_name in find_worker_state.metaworkers:
            continue

        try:
            if new_module_name not in sys.modules:
                if file_path.endswith(".spy"):
                    #importing like this is not a good idea...
                    # __import__(new_module_name)
                    raise Exception

                elif opener is not None:
                    __import__(new_module_name)
                    sys.modules[new_module_name].__file__ = file_path

                else:
                    fil = open(file_path, "r")
                    imp.load_module(new_module_name, fil, file_path, ("py", "r", imp.PY_SOURCE))

        except Exception:
            print("Error in importing", new_module_name)
            traceback.print_exc()
            continue

        new_module = sys.modules[new_module_name]
        search_path = new_module.__file__.endswith("__init__.pyc") or module.__file__.endswith("__init__.py")
        new_find_worker_state = find_workers(new_module, new_module_name, done_mods, found_workers,
                                             search_path=search_path, lister=lister, opener=opener)
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
                if l.startswith("#"):
                    continue
                if not len(l):
                    continue
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

    def __init__(self, location_modules, syspath, found_workers=None, lister=None, opener=None):
        self.lister = lister
        self.opener = opener
        self._done_mods = set()
        self._found_workers = set()

        if found_workers is not None:
            for worker in found_workers:
                self._found_workers.add(worker)

        find_worker_state = FindWorkerState()
        syspath_backup = list(sys.path)
        sys.path = syspath

        for module in location_modules:
            star = False
            if module.endswith(".*"):
                star = True
                module = module[:-2]

            try:
                if module not in sys.modules:
                    __import__(module)
                    print("OPEN", module)

                mod = sys.modules[module]
                if mod.__file__.endswith(".spy"):
                    continue

                search_path = mod.__file__.endswith("__init__.pyc") or mod.__file__.endswith("__init__.py")
                new_find_worker_state = find_workers(mod, module, self._done_mods, self._found_workers, star,
                                                     search_path=search_path, lister=self.lister, opener=self.opener)
                find_worker_state.update(new_find_worker_state)

            except:
                print("Error in importing", module)
                traceback.print_exc()

        sys.path = syspath_backup

        for worker_name, variable_name, worker in find_worker_state.suspect:
            if id(worker) in self._found_workers:
                continue

            worker_path = worker.__module__ + "." + variable_name
            if worker_path in find_worker_state.workers or worker_path in find_worker_state.metaworkers:
                continue

            add_worker(worker, worker_name, find_worker_state, self._found_workers)

        self.workers = find_worker_state.workers
        self.metaworkers = find_worker_state.metaworkers
        self.hivemapworkers = find_worker_state.hivemap_workers
        self.spydermapworkers = find_worker_state.spydermap_workers
        self.drones = find_worker_state.drones
        self.spyderhives = find_worker_state.spyderhives
        self.typelist = set()

        for worker in self.workers.values():
            gui_params = worker.guiparams
            worker_types = list(gui_params.get("antennas", {}).values()) + list(gui_params.get("outputs", {}).values())

            for worker_type in worker_types:
                self.typelist.add(worker_type[1])
