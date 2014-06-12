from __future__ import print_function, absolute_import

"""
Manages the finding and building of worker templates
 and the instantiation of workers and worker parameters
"""
import os, functools
from . import WorkerFinder
from ..params import parse_paramtypelist, get_param_pullantennas


class WorkerManager(object):
    _workerfinderclass = WorkerFinder

    def __init__(self,
                 workerbuilder, workerinstancemanager, pmanager,
                 pworkercreator, pdronecreator=None,
                 with_blocks=True
    ):
        self._workerbuilder = workerbuilder
        self._wim = workerinstancemanager
        self._wim.observers_selection.append(self.gui_selects)
        self._wim.observers_remove.append(self.gui_removes)
        self._pmanager = pmanager
        self._pworkercreator = pworkercreator
        self._pdronecreator = pdronecreator
        self._workerfinder_global = None
        self._workerfinder_local = None
        self._worker_parameters = {}
        self._worker_metaparameters = {}
        self._antennafoldstate = None
        self._typelist_listeners = []
        self._used_typelist = set()
        self._with_blocks = with_blocks

    def set_antennafoldstate(self, antennafoldstate):
        self._antennafoldstate = antennafoldstate

    def _remove_workerfinder(self, wf):
        if wf is not None:
            workers = wf.workers
            for workername in sorted(workers.keys()):
                self._workerbuilder.remove_worker(workername)
            metaworkers = wf.metaworkers
            for metaworkername in sorted(metaworkers.keys()):
                self._workerbuilder.remove_metaworker(metaworkername)

    def add_typelist_listener(self, listener):
        self._typelist_listeners.append(listener)

    def _update_typelist(self):
        typelist = set()
        typelist.update(self._used_typelist)
        wfg = self._workerfinder_global
        if wfg is not None:
            typelist.update(wfg.typelist)
        wfl = self._workerfinder_local
        if wfl is not None:
            typelist.update(wfl.typelist)
        for tl in self._typelist_listeners:
            tl(typelist)

    def _find_global_workers(self, hiveguidir, locationconfs, remove):
        if remove:
            self._remove_workerfinder(self._workerfinder_global)

        wfc = self._workerfinderclass
        locationmodules, syspath = \
            wfc.find_locationmodules(locationconfs)
        self._workerfinder_global = wfc(locationmodules, [hiveguidir] + syspath)

    def _find_local_workers(self, localconfs, localdir):
        self._remove_workerfinder(self._workerfinder_local)

        localconfs = [p for p in localconfs if os.path.exists(p)]
        wfc = self._workerfinderclass
        locationmodules, syspath = \
            wfc.find_locationmodules(localconfs, localdir)
        found = self._workerfinder_global._found_workers
        self._workerfinder_local = wfc(locationmodules, syspath, found)

    def find_global_workers(self, currdir, hiveguidir, remove=True):
        locationconfs = [currdir + os.sep + "locations.conf"]
        self._find_global_workers(hiveguidir, locationconfs, remove)
        self._update_typelist()

    def find_local_workers(self, localdir=None):
        if localdir is None or localdir == "": localdir = os.getcwd()
        localconfs = [localdir + os.sep + "hivegui.conf"]
        self._find_local_workers(localconfs, localdir)
        self._update_typelist()

    def get_spyderhives(self):
        ret = {}
        for wf in (self._workerfinder_global, self._workerfinder_local):
            if wf is None: continue
            ret.update(wf.spyderhives)
        return ret

    def build_workers(self, local):
        if local:
            wf = self._workerfinder_local
        else:
            wf = self._workerfinder_global
        workers = wf.workers
        for workername in sorted(workers.keys()):
            worker = workers[workername]
            self._workerbuilder.build_worker(workername, worker)
            self._pworkercreator.append(workername)
        metaworkers = wf.metaworkers
        for metaworkername in sorted(metaworkers.keys()):
            metaworker = metaworkers[metaworkername]
            self._workerbuilder.build_metaworker(metaworkername, metaworker)
            self._pworkercreator.append(metaworkername)
        hivemapworkers = wf.hivemapworkers
        for hivemapworkername in sorted(hivemapworkers.keys()):
            hivemapworker = hivemapworkers[hivemapworkername]
            self._workerbuilder.build_hivemapworker(hivemapworkername, hivemapworker)
            self._pworkercreator.append(hivemapworkername)
        spydermapworkers = wf.spydermapworkers
        for spydermapworkername in sorted(spydermapworkers.keys()):
            spydermapworker = spydermapworkers[spydermapworkername]
            self._pworkercreator.append(spydermapworkername)
        if self._pdronecreator is not None:
            drones = wf.drones
            for dronename in sorted(drones.keys()):
                drone = drones[dronename]
                self._pdronecreator.append(dronename)

    def build_worker(self, workername):
        found = False
        for wf in (self._workerfinder_local, self._workerfinder_global):
            if wf is None: continue
            if workername in wf.workers:
                worker = wf.workers[workername]
                self._workerbuilder.build_worker(workername, worker)
                self._pworkercreator.append(workername)
                found = True
                break
            elif workername in wf.metaworkers:
                metaworker = metaworkers[metaworkername]
                self._workerbuilder.build_metaworker(metaworkername, metaworker)
                self._pworkercreator.append(metaworkername)
                found = True
                break

        if not found: raise KeyError(workername)

    def remove_built_worker(self, workername):
        if self._workerbuilder.has_worker(workername):
            self._workerbuilder.remove_worker(workername)
        elif self._workerbuilder.has_metaworker(workername):
            self._workerbuilder.remove_metaworker(workername)
        else:
            raise KeyError(workername)
        self._pworkercreator.remove(workername)

    def instantiate(self,
                    workerid, workertype, x, y,
                    metaparamvalues=None, paramvalues=None,
                    clash_offset=None
    ):
        assert workerid not in self._worker_parameters, workerid

        if workertype.startswith("<drone>:"):
            wi = self._workerbuilder.get_droneinstance()
        elif workertype.find("#") > -1:
            wi = self._workerbuilder.get_zeroinstance()
        elif self._workerbuilder.has_worker(workertype):
            wi = self._workerbuilder.get_workerinstance(workertype)
            assert metaparamvalues is None \
                   or len(metaparamvalues) == 0
        elif self._workerbuilder.has_metaworker(workertype):
            if metaparamvalues is None:
                metaparamvalues = {}
            tt = self._workerbuilder.build_worker_from_meta(
                workertype, metaparamvalues
            )
            self._worker_metaparameters[workerid] = [workertype, tt[0], tt[1], tt[2], tt[3]]
            worker = tt[0]
            wi = worker.primary_instance

            # check if we are using some type for the first time...
            mparamnames, mparamtypelist, mparams = tt[1], tt[2], tt[3]
            for mparamname, mparamtype in zip(mparamnames, mparamtypelist):
                mparam = mparams.get(mparamname, None)
                if mparam is None: continue
                ok = False
                if mparamtype == "type":
                    ok = True
                elif isinstance(mparamtype, tuple):
                    if mparamtype[0] == "type":
                        ok = True
                    elif isinstance(mparamtype[0], tuple):
                        if mparamtype[0][0] == "type": ok = True
                if not ok: continue
                t = mparam
                if t not in self._used_typelist:
                    self._used_typelist.add(t)
                    self._update_typelist()

        else:
            raise KeyError(workertype)

        # clash offset adds an offset if an existing node is within one pixel
        if clash_offset is not None:
            cx, cy = clash_offset
            nodexy = []
            for wid in self.workerids():
                if wid == workerid: continue
                node = self._wim.get_node(wid)[0]
                nx, ny = node.position
                nodexy.append((nx, ny))
            while 1:
                for nx, ny in nodexy:
                    if \
                                                            nx < x - 1 or \
                                                            nx > x + 1 or \
                                                    ny < y - 1 or \
                                            ny > y + 1:
                        continue
                    x += cx
                    y += cy
                    break
                else:
                    break
        self._wim.add_workerinstance(workerid, wi, x, y)

        pvalues = {}
        if paramvalues is not None:
            arglist = []
            for paramname in wi.paramnames:
                v = paramvalues.get(paramname, None)
                arglist.append(v)
            args = parse_paramtypelist(wi.paramtypelist, arglist)
            for paramname, a in zip(wi.paramnames, args):
                if a is not None: pvalues[paramname] = a
        self._worker_parameters[workerid] = [workertype, wi.paramnames, wi.paramtypelist, pvalues, wi.guiparams]
        if self._antennafoldstate is not None:
            gp = {}
            pullantennas = []
            if wi.guiparams is not None:
                gp = wi.guiparams.get("guiparams", {})
                antennas = wi.guiparams.get("antennas", {})
                pullantennas = get_param_pullantennas(antennas)
            self._antennafoldstate.create_worker(
                workerid,
                pullantennas,
                gp,
            )
        self._wim.set_parameters(workerid, pvalues)

    def _select(self, workerids):
        self._pmanager.deselect()
        if workerids is None: return
        if len(workerids) == 1:
            workerid = workerids[0]
            pwin_general = self._pmanager.get_pwindow("general")
            pwin_general.load_paramset(workerid)
            if workerid in self._worker_parameters:
                self._pwindow_select_worker_params(workerid)
            if workerid in self._worker_metaparameters:
                self._pwindow_select_worker_metaparams(workerid)
            if self._with_blocks:
                pwin_block = self._pmanager.get_pwindow("block")
                pwin_block.load_paramset(workerid)

    def select(self, workerids):
        self._wim.select(workerids)
        self._select(workerids)

    def gui_selects(self, workerids):
        self._select(workerids)

    def _pwindow_select_worker_params(self, workerid):
        params = self._worker_parameters[workerid]
        workertype = params[0]
        pullantennas = []
        wi = self._wim.get_workerinstance(workerid)
        if wi.guiparams is not None:
            pullantennas = get_param_pullantennas(wi.guiparams.get("antennas", {}))
            pullantennas = [p[0] for p in pullantennas]
        pureparams = [p for p in params[1] if p not in pullantennas]
        up = functools.partial(
            self._update_worker_parameters, workerid, pureparams
        )
        metaparams = None
        if workerid in self._worker_metaparameters:
            metaparams = self._worker_metaparameters[workerid][4]
        form_manipulators = self._workerbuilder.get_form_manipulators(workertype, metaparams)
        if self._antennafoldstate is not None:
            f = functools.partial(self._antennafoldstate.init_form, workerid)
            form_manipulators = form_manipulators + [f]
        widget, controller = self._pmanager.select_pwidget(workerid, "params",
                                                           params[1], params[2], params[3], up, [], form_manipulators
        )
        if widget is not None and self._antennafoldstate is not None:
            self._antennafoldstate.init_widget(workerid, widget, controller)

    def _pwindow_select_worker_metaparams(self, workerid):
        params = self._worker_metaparameters[workerid]
        inst = functools.partial(
            self.instantiate_from_meta, workerid, params[0]
        )
        buttons = [("Create instance", inst)]
        up = functools.partial(
            self._update_worker_metaparameters, workerid
        )
        form_manipulators = self._workerbuilder.get_form_manipulators(params[0], None)
        self._pmanager.select_pwidget(workerid, "metaparams",
                                      params[2], params[3], params[4], up, buttons, form_manipulators
        )

    def get_new_empty_workerid(self):
        n = 0
        while 1:
            n += 1
            id_ = "<empty%d>" % n
            if id_ in self._worker_parameters: continue
            if id_ in self._worker_metaparameters: continue
            return id_

    def get_new_workerid(self, workertype):
        n = 0
        if workertype.find(":") > -1:
            template = workertype.split(":")[-1].split(".")[-2]
        elif workertype.find("#") > -1:
            template = workertype.split("#")[-1].split(".")[-2]
        else:
            template = workertype.split(".")[-1]
        tt = template.split("_")
        if len(tt) > 1:
            try:
                int(tt[-1])
            except ValueError:
                pass
            else:
                template = "_".join(tt[:-1])
        while 1:
            n += 1
            id_ = "%s_%d" % (template, n)
            if id_ in self._worker_parameters: continue
            if id_ in self._worker_metaparameters: continue
            return id_

    def get_new_connection_id(self, template):
        n = 0
        tt = template.split("_")
        con_ids = self._wim.get_connection_ids()
        if len(tt) > 1:
            try:
                int(tt[-1])
            except ValueError:
                pass
            else:
                template = "_".join(tt[:-1])
        while 1:
            n += 1
            id_ = "%s_%d" % (template, n)
            if id_ in con_ids: continue
            return id_

    def meta_empty_instantiate(self, workerid, workertype, x, y):
        t = self._workerbuilder.get_metaworker(workertype)
        self._worker_metaparameters[workerid] = [workertype, None, t[1], t[2], {}]
        self._wim.add_empty(workerid, x, y)

    def instantiate_from_meta(self, workerid, workertype, metaparamvalues):
        if metaparamvalues is None:
            print("Cannot instantiate metaworker '%s' (%s): invalid meta-parameters" \
                  % (workerid, workertype))
            return
        try:
            node = self._wim.get_node(workerid)[0]
        except KeyError:
            print("Cannot instantiate metaworker '%s' (%s): empty no longer exists" \
                  % (workerid, workertype))
            return
        x, y = node.position

        # first see if this doesn't raise an exception...
        self._workerbuilder.build_worker_from_meta(
            workertype, metaparamvalues
        )

        # all set, there should be no exceptions now
        if workerid in self._worker_parameters:  #re-instantiation, delete the old worker
            #TODO: re-form connections of the old worker, and restore parameters, if we can
            self.remove(workerid)
        else:  #the worker was only a shell, instantiating for the first time
            self._wim.remove_empty(workerid)
            self._worker_metaparameters.pop(workerid)
            self._pmanager.delete_pwidget(workerid)
            workerid = self.get_new_workerid(workertype)

        self.instantiate(workerid, workertype, x, y, metaparamvalues)
        if self._antennafoldstate is not None:
            self._antennafoldstate.sync(workerid, onload=False)
        self.select([workerid])

    def _meta_autocreate(self, workertype, workerid, x, y):
        t = self._workerbuilder.get_metaworker(workertype)
        metaguiparams = t[0].metaguiparams
        paramnames = t[1]
        if "autocreate" not in metaguiparams: return False
        autocreate = metaguiparams["autocreate"]
        if not isinstance(autocreate, dict):
            raise ValueError(
                "%s.metaguiparams[\"autocreate\"] must be a dict with default values for all metaparameters, not '%s'" % (
                    workertype, autocreate))
        for p in paramnames:
            if p not in autocreate:
                raise ValueError(
                    "%s.metaguiparams[\"autocreate\"] must be a dict with default values for all metaparameters; missing parameter '%s'" % (
                        workertype, p))
        self.instantiate(workerid, workertype, x, y, autocreate)
        return True

    def create(self,
               workerid, workertype, x, y, metaparamvalues=None, paramvalues=None
    ):
        assert workerid not in self._worker_parameters, workerid

        if metaparamvalues == {}:
            metaparamvalues = None
        if paramvalues == {}:
            paramvalues = None

        if metaparamvalues is None and self._workerbuilder.has_metaworker(workertype):
            assert paramvalues is None
            autocreate = self._meta_autocreate(workertype, workerid, x, y)
            if autocreate:
                if self._antennafoldstate is not None:
                    self._antennafoldstate.sync(workerid, onload=False)
                return workerid
            empty_workerid = self.get_new_empty_workerid()
            self.meta_empty_instantiate(empty_workerid, workertype, x, y)
            return empty_workerid
        else:
            self.instantiate(workerid, workertype, x, y, metaparamvalues, paramvalues)
            if self._antennafoldstate is not None:
                self._antennafoldstate.sync(workerid, onload=False)
            return workerid

    def create_drone(self, workerid, dronetype, x, y, paramvalues=None):
        assert workerid not in self._worker_parameters, workerid
        workertype = "<drone>:" + dronetype
        if paramvalues is not None:
            paramvalues = dict(zip(["arg1", "arg2", "arg3", "arg4", "arg5"], paramvalues))
        self.instantiate(workerid, workertype, x, y, paramvalues=paramvalues)
        return workerid

    def create_spydermap(self, workerid, workertype, x, y):
        assert workerid not in self._worker_parameters, workerid
        self.instantiate(workerid, workertype, x, y)
        return workerid

    def _remove(self, workerid):
        self._pmanager.delete_pwidget(workerid)
        self._worker_parameters.pop(workerid, None)
        if self._antennafoldstate is not None:
            self._antennafoldstate.remove_worker(workerid)
        m = self._worker_metaparameters.pop(workerid, None)
        if m is not None:
            worker = m[1]

    def remove(self, workerid):
        self._remove(workerid)
        self._wim.remove_workerinstance(workerid)

    def gui_removes(self, workerid):
        self._remove(workerid)
        self._wim.gui_removes_workerinstance(workerid)

    def _rename_worker(self, old_workerid, new_workerid):
        for dic in (self._worker_parameters, self._worker_metaparameters):
            if old_workerid in dic:
                if new_workerid in dic: return False
        for dic in (self._worker_parameters, self._worker_metaparameters):
            if old_workerid in dic:
                params = dic.pop(old_workerid)
                dic[new_workerid] = params
        return True

    def rename_worker(self, old_workerid, new_workerid):
        ok = self._rename_worker(old_workerid, new_workerid)
        if not ok:
            raise ValueError("workerid already exists: '%s'" % new_workerid)
        self._pmanager.rename_pwidget(old_workerid, new_workerid)
        self._wim.rename_workerinstance(old_workerid, new_workerid)
        if self._antennafoldstate is not None:
            self._antennafoldstate.rename_worker(old_workerid, new_workerid)

    def gui_renames_worker(self, old_workerid, new_workerid):
        """
        Worker has been renamed by the PGui, not the canvas...
        """
        ok = self._rename_worker(old_workerid, new_workerid)
        if not ok: return False
        self._wim.rename_workerinstance(old_workerid, new_workerid)
        if self._antennafoldstate is not None:
            self._antennafoldstate.rename_worker(old_workerid, new_workerid)
        return True

    def _update_worker_parameters(self, workerid, paramnames, parameters):
        # print("UP", workerid, parameters)
        params_old = self._worker_parameters[workerid][3]
        if parameters is None:
            if params_old is None: return
            parameters = {}
        else:
            paramcopy = {}
            for p in parameters:
                if p in paramnames: paramcopy[p] = parameters[p]
            parameters = paramcopy
        self._wim.set_parameters(workerid, parameters)
        self._worker_parameters[workerid][3] = parameters

    def _update_worker_metaparameters(self, workerid, parameters):
        # print("UPM", workerid, parameters)
        if parameters is None: return  # TODO: may not be the sane thing to do
        self._worker_metaparameters[workerid][4] = parameters

    def _update_variable(self, varid, value):
        self._update_worker_parameters(varid, ["value"], {"value": value})

    def get_worker_descriptor(self, workerid):
        node, mapping = self._wim.get_node(workerid)
        if node.empty: return None
        inst = self._wim.get_workerinstance(workerid)
        profile = inst.curr_profile
        gp = inst.guiparams
        workertype, params, metaparams = self.get_parameters(workerid)
        x, y = node.position
        desc = (workerid, workertype, x, y, metaparams, params, profile, gp)
        return desc

    def workerids(self):
        return sorted(
            list(
                set(self._worker_metaparameters.keys()).union(
                    set(self._worker_parameters.keys())
                )
            )
        )

    def get_parameters(self, workerid):
        assert workerid in self._worker_parameters or \
               workerid in self._worker_metaparameters
        workertype, params, metaparams = None, None, None

        if workerid in self._worker_parameters:
            p = self._worker_parameters[workerid]
            workertype = p[0]
            params = p[3]
            if len(params) == 0: params = None
        if workerid in self._worker_metaparameters:
            p = self._worker_metaparameters[workerid]
            workertype = p[0]
            metaparams = p[4]
            if len(metaparams) == 0: metaparams = None
        return workertype, params, metaparams

    def clear_workers(self):
        for workerid in self.workerids():
            self.remove(workerid)

    def get_wim(self):
        return self._wim

    def get_block(self, workerid):
        assert self._with_blocks == True
        if workerid in self._worker_metaparameters:
            worker = self._worker_metaparameters[workerid][1]
            if worker is None: return None
            return worker.block
        else:
            workertype = self._worker_parameters[workerid][0]
            if workertype.startswith("<drone>:"): return None
            if workertype.find("#") > -1: return None
            return self._workerbuilder.get_block(workertype)

    def get_workertemplate(self, workerid):
        if workerid in self._worker_metaparameters:
            worker = self._worker_metaparameters[workerid][1]
            if worker is None: return None
            return worker
        else:
            workertype = self._worker_parameters[workerid][0]
            return self._workerbuilder.get_workertemplate(workertype)

    def unbuild_local_workers(self):
        wf = self._workerfinder_local
        if wf is None: return

        workers = wf.workers
        for workername in sorted(workers.keys()):
            self._workerbuilder.remove_worker(workername)
            self._pworkercreator.remove(workername)
        hivemapworkers = wf.hivemapworkers
        for hivemapworkername in sorted(hivemapworkers.keys()):
            self._workerbuilder.remove_worker(hivemapworkername)
            self._pworkercreator.remove(hivemapworkername)
        spydermapworkers = wf.spydermapworkers
        for spydermapworkername in sorted(spydermapworkers.keys()):
            self._pworkercreator.remove(spydermapworkername)
        metaworkers = wf.metaworkers
        for metaworkername in sorted(metaworkers.keys()):
            self._workerbuilder.remove_metaworker(metaworkername)
            self._pworkercreator.remove(metaworkername)
        drones = wf.drones
        for dronename in sorted(drones.keys()):
            self._pdronecreator.remove(dronename)

        self._workerfinder_local = None

    def sync_antennafoldstate(self):
        if self._antennafoldstate is None: return
        for workerid in self._wim.get_workerinstances():
            self._antennafoldstate.sync(workerid, onload=True)