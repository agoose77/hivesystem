from __future__ import print_function, absolute_import

"""
Manages the finding and building of worker templates
 and the instantiation of workers and worker parameters
"""
import os, functools
from . import WorkerFinder
from .. import PersistentIDManager
from ..params import parse_paramtypelist, get_param_pullantennas


class WorkerManager(object):
    _workerfinderclass = WorkerFinder

    def __init__(self, workerbuilder, workerinstancemanager, pmanager, pworkercreator, pdronecreator=None,
                 with_blocks=True):
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
        self._persistent_id_manager = PersistentIDManager()

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

    def instantiate(self, worker_id, workertype, x, y, metaparamvalues=None, paramvalues=None, clash_offset=None):
        assert worker_id not in self._worker_parameters, worker_id
        if workertype.startswith("<drone>:"):
            worker_instance = self._workerbuilder.get_droneinstance()

        elif workertype.find("#") > -1:
            worker_instance = self._workerbuilder.get_zeroinstance()

        elif self._workerbuilder.has_worker(workertype):
            worker_instance = self._workerbuilder.get_workerinstance(workertype)
            assert metaparamvalues is None or len(metaparamvalues) == 0

        elif self._workerbuilder.has_metaworker(workertype):
            if metaparamvalues is None:
                metaparamvalues = {}

            meta_worker_data = self._workerbuilder.build_worker_from_meta(
                workertype, metaparamvalues
            )
            self._worker_metaparameters[worker_id] = [workertype, meta_worker_data[0], meta_worker_data[1], meta_worker_data[2], meta_worker_data[3]]
            worker = meta_worker_data[0]
            worker_instance = worker.primary_instance

            # check if we are using some type for the first time...
            mparamnames, mparamtypelist, mparams = meta_worker_data[1], meta_worker_data[2], meta_worker_data[3]
            for mparamname, mparamtype in zip(mparamnames, mparamtypelist):
                mparam = mparams.get(mparamname, None)
                if mparam is None:
                    continue

                ok = False
                if mparamtype == "type":
                    ok = True

                elif isinstance(mparamtype, tuple):
                    if mparamtype[0] == "type":
                        ok = True

                    elif isinstance(mparamtype[0], tuple):
                        if mparamtype[0][0] == "type":
                            ok = True

                if not ok:
                    continue

                type_ = mparam
                if type_ not in self._used_typelist:
                    self._used_typelist.add(type_)
                    self._update_typelist()

        else:
            raise KeyError(workertype)

        # clash offset adds an offset if an existing node is within one pixel
        if clash_offset is not None:
            cx, cy = clash_offset
            nodexy = []
            for wid in self.workerids():
                if wid == worker_id: continue
                node = self._wim.get_node(wid)[0]
                nx, ny = node.position
                nodexy.append((nx, ny))

            while 1:
                for nx, ny in nodexy:
                    if (nx < x - 1) or (nx > x + 1) or (ny < y - 1) or (ny > y + 1):
                        continue
                    x += cx
                    y += cy
                    break

                else:
                    break

        self._wim.add_workerinstance(worker_id, worker_instance, x, y)

        parameter_values = {}
        if paramvalues is not None:
            argument_list = []
            for parameter_name in worker_instance.paramnames:
                parameter_value = paramvalues.get(parameter_name, None)
                argument_list.append(parameter_value)

            arguments = parse_paramtypelist(worker_instance.paramtypelist, argument_list)

            for parameter_name, argument in zip(worker_instance.paramnames, arguments):
                if argument is not None:
                    parameter_values[parameter_name] = argument

        self._worker_parameters[worker_id] = [workertype, worker_instance.paramnames, worker_instance.paramtypelist, parameter_values, worker_instance.guiparams]
        if self._antennafoldstate is not None:
            gp = {}
            pullantennas = []
            if worker_instance.guiparams is not None:
                gp = worker_instance.guiparams.get("guiparams", {})
                antennas = worker_instance.guiparams.get("antennas", {})
                pullantennas = get_param_pullantennas(antennas)
            self._antennafoldstate.create_worker(worker_id, pullantennas, gp)

        self._wim.set_parameters(worker_id, parameter_values)

        self._persistent_id_manager.create_persistent_id(worker_id)

    def _select(self, worker_ids):
        self._pmanager.deselect()
        if worker_ids is None:
            return

        for worker_id in worker_ids:
            pwin_general = self._pmanager.get_pwindow("general")
            pwin_general.load_paramset(worker_id)
            if worker_id in self._worker_parameters:
                self._pwindow_select_worker_params(worker_id)
            if worker_id in self._worker_metaparameters:
                self._pwindow_select_worker_metaparams(worker_id)
            if self._with_blocks:
                pwin_block = self._pmanager.get_pwindow("block")
                pwin_block.load_paramset(worker_id)

    def select(self, worker_ids):
        self._wim.select(worker_ids)
        self._select(worker_ids)

    def gui_selects(self, worker_ids):
        self._select(worker_ids)

    def _pwindow_select_worker_params(self, worker_id):
        params = self._worker_parameters[worker_id]
        workertype = params[0]
        pullantennas = []
        wi = self._wim.get_workerinstance(worker_id)
        if wi.guiparams is not None:
            pullantennas = get_param_pullantennas(wi.guiparams.get("antennas", {}))
            pullantennas = [p[0] for p in pullantennas]

        pureparams = [p for p in params[1] if p not in pullantennas]
        # Unchanging persistent ID
        mvc_id = self._persistent_id_manager.get_persistent_id(worker_id)

        def update_function(parameters):
            _worker_id = self._persistent_id_manager.get_temporary_id(mvc_id)
            self._update_worker_parameters(_worker_id, pureparams, parameters)

        def form_function(form):
            _worker_id = self._persistent_id_manager.get_temporary_id(mvc_id)
            self._antennafoldstate.init_form(_worker_id, form)

        metaparams = None
        if worker_id in self._worker_metaparameters:
            metaparams = self._worker_metaparameters[worker_id][4]

        form_manipulators = self._workerbuilder.get_form_manipulators(workertype, metaparams)
        if self._antennafoldstate is not None:
            form_manipulators = form_manipulators + [form_function]

        widget, controller = self._pmanager.select_pwidget(worker_id, "params", params[1], params[2],  params[3],
                                                           update_function, [], form_manipulators)
        print("SELCT")
        if widget is not None and self._antennafoldstate is not None:
            self._antennafoldstate.init_widget(worker_id, widget, controller)

    def _pwindow_select_worker_metaparams(self, worker_id):
        params = self._worker_metaparameters[worker_id]
        inst = functools.partial(
            self.instantiate_from_meta, worker_id, params[0]
        )
        buttons = [("Create instance", inst)]
        up = functools.partial(
            self._update_worker_metaparameters, worker_id
        )
        form_manipulators = self._workerbuilder.get_form_manipulators(params[0], None)
        self._pmanager.select_pwidget(worker_id, "metaparams",
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

    def meta_empty_instantiate(self, worker_id, workertype, x, y):
        t = self._workerbuilder.get_metaworker(workertype)
        self._worker_metaparameters[worker_id] = [workertype, None, t[1], t[2], {}]
        self._wim.add_empty(worker_id, x, y)

    def instantiate_from_meta(self, worker_id, workertype, metaparamvalues):
        if metaparamvalues is None:
            print("Cannot instantiate metaworker '%s' (%s): invalid meta-parameters" \
                  % (worker_id, workertype))
            return
        try:
            node = self._wim.get_node(worker_id)[0]
        except KeyError:
            print("Cannot instantiate metaworker '%s' (%s): empty no longer exists" \
                  % (worker_id, workertype))
            return
        x, y = node.position

        # first see if this doesn't raise an exception...
        self._workerbuilder.build_worker_from_meta(
            workertype, metaparamvalues
        )

        # all set, there should be no exceptions now
        already_existed = worker_id in self._worker_parameters
        if already_existed:  #re-instantiation, delete the old worker
            #Re-form connections of the old worker, and restore parameters, if we can
            all_connections = self._wim.get_connections()
            worker_connections = []
            for connection in all_connections:
                if connection.start_node == worker_id:
                    worker_connections.append(connection)
                elif connection.end_node == worker_id:
                    worker_connections.append(connection)

            self.remove(worker_id)

        else:  #the worker was only a shell, instantiating for the first time
            self._wim.remove_empty(worker_id)
            self._worker_metaparameters.pop(worker_id)
            self._pmanager.delete_pwidget(worker_id)
            worker_id = self.get_new_workerid(workertype)

        self.instantiate(worker_id, workertype, x, y, metaparamvalues)
        if already_existed:
            for connection in worker_connections:
                con_id = self.get_new_connection_id("con")

                start = connection.start_node
                end = connection.end_node

                try:
                    self._wim.add_connection(con_id, (start, connection.start_attribute),
                                             (end, connection.end_attribute), connection.interpoints)
                except KeyError:
                    import traceback
                    traceback.print_exc()
                    continue

                else:
                    print(start, end, "NEW")
        print("DONE")
        self.select([worker_id])

    def _meta_autocreate(self, workertype, worker_id, x, y):
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
        self.instantiate(worker_id, workertype, x, y, autocreate)
        return True

    def create(self, worker_id, workertype, x, y, metaparamvalues=None, paramvalues=None):
        assert worker_id not in self._worker_parameters, worker_id

        if metaparamvalues == {}:
            metaparamvalues = None
        if paramvalues == {}:
            paramvalues = None

        if metaparamvalues is None and self._workerbuilder.has_metaworker(workertype):
            assert paramvalues is None
            autocreate = self._meta_autocreate(workertype, worker_id, x, y)
            if autocreate:
                return worker_id

            empty_worker_id = self.get_new_empty_workerid()
            self.meta_empty_instantiate(empty_worker_id, workertype, x, y)
            return empty_worker_id

        else:
            self.instantiate(worker_id, workertype, x, y, metaparamvalues, paramvalues)
            return worker_id

    def create_drone(self, worker_id, dronetype, x, y, paramvalues=None):
        assert worker_id not in self._worker_parameters, worker_id
        workertype = "<drone>:" + dronetype
        if paramvalues is not None:
            paramvalues = dict(zip(["arg1", "arg2", "arg3", "arg4", "arg5"], paramvalues))
        self.instantiate(worker_id, workertype, x, y, paramvalues=paramvalues)
        return worker_id

    def create_spydermap(self, worker_id, workertype, x, y):
        assert worker_id not in self._worker_parameters, worker_id
        self.instantiate(worker_id, workertype, x, y)
        return worker_id

    def _remove(self, worker_id):
        print("REMOVE")
        self._pmanager.delete_pwidget(worker_id)
        self._worker_parameters.pop(worker_id, None)
        if self._antennafoldstate is not None:
            self._antennafoldstate.remove_worker(worker_id)
        m = self._worker_metaparameters.pop(worker_id, None)
        if m is not None:
            worker = m[1]

    def remove(self, worker_id):
        if not worker_id in self._antennafoldstate.states:
            return
        self._remove(worker_id)
        self._wim.remove_workerinstance(worker_id)

    def gui_removes(self, worker_id):
        self._remove(worker_id)
        self._wim.gui_removes_workerinstance(worker_id)

    def _rename_worker(self, old_worker_id, new_worker_id):
        for dic in (self._worker_parameters, self._worker_metaparameters):
            if old_worker_id in dic:
                if new_worker_id in dic:
                    return False

        for dic in (self._worker_parameters, self._worker_metaparameters):
            if old_worker_id in dic:
                params = dic.pop(old_worker_id)
                dic[new_worker_id] = params

        # Update the persistent ID
        self._persistent_id_manager.change_temporary_with_temporary_id(old_worker_id, new_worker_id)

        return True

    def rename_worker(self, old_worker_id, new_worker_id):
        ok = self._rename_worker(old_worker_id, new_worker_id)
        if not ok:
            raise ValueError("worker_id already exists: '%s'" % new_worker_id)

        self._pmanager.rename_pwidget(old_worker_id, new_worker_id)
        self._wim.rename_workerinstance(old_worker_id, new_worker_id)

        if self._antennafoldstate is not None:
            self._antennafoldstate.rename_worker(old_worker_id, new_worker_id)

    def gui_renames_worker(self, old_worker_id, new_worker_id):
        """
        Worker has been renamed by the PGui, not the canvas...
        """
        ok = self._rename_worker(old_worker_id, new_worker_id)
        if not ok:
            return False

        self._wim.rename_workerinstance(old_worker_id, new_worker_id)

        if self._antennafoldstate is not None:
            self._antennafoldstate.rename_worker(old_worker_id, new_worker_id)
        return True

    def _update_worker_parameters(self, worker_id, paramnames, parameters):
        params_old = self._worker_parameters[worker_id][3]

        if parameters is None:
            if params_old is None:
                return

            parameters = {}

        else:
            parameters_copy = {}
            for parameter_name in parameters:
                if parameter_name in paramnames:
                    parameters_copy[parameter_name] = parameters[parameter_name]

            parameters = parameters_copy

        self._wim.set_parameters(worker_id, parameters)
        self._worker_parameters[worker_id][3] = parameters

    def _update_worker_metaparameters(self, worker_id, parameters):
        # print("UPM", worker_id, parameters)
        if parameters is None: return  # TODO: may not be the sane thing to do
        self._worker_metaparameters[worker_id][4] = parameters

    def _update_variable(self, varid, value):
        self._update_worker_parameters(varid, ["value"], {"value": value})

    def get_worker_descriptor(self, worker_id):
        node, mapping = self._wim.get_node(worker_id)
        if node.empty:
            return None
        inst = self._wim.get_workerinstance(worker_id)
        profile = inst.curr_profile
        gp = inst.guiparams
        if gp is None:
            gp = {}

        workertype, params, metaparams = self.get_parameters(worker_id)
        x, y = node.position
        desc = (worker_id, workertype, x, y, metaparams, params, profile, gp)
        return desc

    def get_worker_connections(self, worker_id):
        wim = self._wim
        connections = []
        for connection in wim.get_connections():
            if connection.start_node == worker_id or connection.end_node == worker_id:
                connections.append(connection)
        return connections

    def get_expanded_antennas(self, worker_id):
        state = self._antennafoldstate.states[worker_id]
        expanded_variables = set()

        if state is None:
            return expanded_variables

        for antenna_name in state:
            antenna = state[antenna_name]
            if antenna.is_folded:
                continue

            expanded_variables.add(antenna_name)

        return expanded_variables

    def workerids(self):
        return sorted(
            list(
                set(self._worker_metaparameters.keys()).union(
                    set(self._worker_parameters.keys())
                )
            )
        )

    def get_parameters(self, worker_id):
        assert worker_id in self._worker_parameters or \
               worker_id in self._worker_metaparameters
        workertype, params, metaparams = None, None, None

        if worker_id in self._worker_parameters:
            p = self._worker_parameters[worker_id]
            workertype = p[0]
            params = p[3]
            if len(params) == 0: params = None
        if worker_id in self._worker_metaparameters:
            p = self._worker_metaparameters[worker_id]
            workertype = p[0]
            metaparams = p[4]
            if len(metaparams) == 0: metaparams = None
        return workertype, params, metaparams

    def clear_workers(self):
        for worker_id in self.workerids():
            self.remove(worker_id)

    def get_wim(self):
        return self._wim

    def get_block(self, worker_id):
        assert self._with_blocks == True
        if worker_id in self._worker_metaparameters:
            worker = self._worker_metaparameters[worker_id][1]
            if worker is None: return None
            return worker.block
        else:
            workertype = self._worker_parameters[worker_id][0]
            if workertype.startswith("<drone>:"): return None
            if workertype.find("#") > -1: return None
            return self._workerbuilder.get_block(workertype)

    def get_workertemplate(self, worker_id):
        if worker_id in self._worker_metaparameters:
            worker = self._worker_metaparameters[worker_id][1]
            if worker is None: return None
            return worker
        else:
            workertype = self._worker_parameters[worker_id][0]
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

    def sync_antennafoldstate(self, worker_ids):
        #raise DeprecationWarning()
        if self._antennafoldstate is None:
            return

        for worker_id in worker_ids:
            self._antennafoldstate.sync(worker_id)