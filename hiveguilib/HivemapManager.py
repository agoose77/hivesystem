from __future__ import print_function, absolute_import
from bee.types import boolparser, spyderparser

import os
import spyder, Spyder


class HivemapManager(object):
    def __init__(self, mainwin, workermanager, workerinstancemanager, file_dialog):
        self._mainwin = mainwin
        self._wim = workerinstancemanager
        self._workermanager = workermanager
        self._file_dialog = file_dialog

        self._lastsave = None

        win = self._mainwin.h()
        win.add_menu("&File")
        win.add_menu_action(
            "&File",
            "&New",
            self.clear,
            shortcut="Ctrl+N",
            statustip="Close the current Hivemap file and open a new one",
        )
        win.add_menu_action(
            "&File",
            "&Open",
            self.menu_load,
            shortcut="Ctrl+O",
            statustip="Open a Hivemap file",
        )
        win.add_menu_action(
            "&File",
            "&Save",
            self.menu_save,
            shortcut="Ctrl+S",
            statustip="Save the current Hivemap file",
        )
        win.add_menu_action(
            "&File",
            "Save as",
            self.menu_save_as,
            statustip="Save the current Hivemap file in the desired location",
        )
        win.add_menu_action(
            "&File",
            "Refresh",
            self.menu_refresh,
            shortcut="F5",
            statustip="Saves and reloads the current Hivemap, refreshing all elements",
        )
        win.add_menu_action(
            "&File",
            "&Quit",
            win.close,
            shortcut="Ctrl+Q",
            statustip="Quits the editor",
        )

    def _load(self, hivemap):
        for w in hivemap.workers:
            x, y = w.position.x, w.position.y
            metaparamvalues = None
            if w.metaparameters is not None:
                metaparamvalues = {}
                for param in w.metaparameters:
                    metaparamvalues[param.pname] = param.pvalue
            paramvalues = None
            if w.parameters is not None:
                paramvalues = {}
                for param in w.parameters:
                    paramvalues[param.pname] = param.pvalue
            try:
                self._workermanager.instantiate(
                    w.workerid, w.workertype, x, y, metaparamvalues, paramvalues
                )
            except KeyError:
                print("Unknown worker:", w.workertype, w.workerid)
                continue
            if w.blockvalues:
                self._wim.worker_update_blockvalues(w.workerid, w.blockvalues)
        if hivemap.drones is not None:
            for d in hivemap.drones:
                x, y = d.position.x, d.position.y
                parameters = d.parameters
                try:
                    self._workermanager.create_drone(
                        d.droneid, d.dronetype, x, y, parameters
                    )
                except KeyError:
                    print("Unknown drone:", d.dronetype, d.droneid)
                    continue
        for con in hivemap.connections:
            con_id = self._workermanager.get_new_connection_id("con")
            interpoints = [(ip.x, ip.y) for ip in con.interpoints]
            self._wim.add_connection(
                con_id,
                (con.start.workerid, con.start.io),
                (con.end.workerid, con.end.io),
                interpoints,
            )
        hmio = hivemap.io
        if hmio is None: hmio = []
        for b in hmio:
            x, y = b.position.x, b.position.y
            target = self._workermanager.get_workertemplate(b.worker)
            if b.io == "antenna":
                try:
                    mode = target.antennas[b.workerio][0]
                except KeyError:
                    assert target.block is not None
                    assert target.block.io == "antenna"
                    mode = target.block.mode
                source = (b.io_id, "outp")
                target = (b.worker, b.workerio)
            else:
                try:
                    mode = target.outputs[b.workerio][0]
                except KeyError:
                    assert target.block is not None
                    assert target.block.io == "output"
                    mode = target.block.mode
                source = (b.worker, b.workerio)
                target = (b.io_id, "inp")
            workertype = "bees.io." + mode + "_" + b.io
            self._workermanager.instantiate(
                b.io_id, workertype, x, y
            )
            con_id = self._workermanager.get_new_connection_id("con")
            self._wim.add_connection(
                con_id,
                source,
                target,
            )

        hmpar = hivemap.parameters
        if hmpar is None: hmpar = []
        for b in hmpar:
            x, y = b.position.x, b.position.y
            workertype = "bees.parameter"
            params = {}
            params["internal_name"] = b.intern_id
            params["typename"] = b.paramtypename
            if b.gui_defaultvalue is not None:
                params["gui_defaultvalue"] = b.gui_defaultvalue
            self._workermanager.instantiate(
                b.extern_id, workertype, x, y, paramvalues=params
            )

        hmat = hivemap.attributes
        if hmat is None: hmat = []
        for b in hmat:
            x, y = b.position.x, b.position.y
            workertype = "bees.attribute"
            metaparams = {"spydertype": b.attrtypename}
            par = spyderparser(b.attrtypename, b.attrvalue)
            params = {"val": par}
            self._workermanager.instantiate(
                b.attr_id, workertype, x, y,
                metaparamvalues=metaparams,
                paramvalues=params
            )

        hmpat = hivemap.pyattributes
        if hmpat is None: hmpat = []
        for b in hmpat:
            x, y = b.position.x, b.position.y
            workertype = "bees.pyattribute"
            params = {}
            params["code"] = b.code
            if b.code_variable is not None:
                params["code_variable"] = b.code_variable
            self._workermanager.instantiate(
                b.attr_id, workertype, x, y, paramvalues=params
            )

        hmparts = hivemap.partbees
        if hmparts is None: hmparts = []
        for b in hmparts:
            x, y = b.position.x, b.position.y
            workertype = "bees.part"
            params = {}
            params["beename"] = b.bee_id
            params["part"] = b.part
            self._workermanager.instantiate(
                b.part_id, workertype, x, y, paramvalues=params
            )

        hmwasps = hivemap.wasps
        if hmwasps is None: hmwasps = []
        for b in hmwasps:
            x, y = b.position.x, b.position.y
            workertype = "bees.wasp"
            params = {}
            params["injected"] = b.injected
            params["target_name"] = b.target
            params["target_parameter"] = b.targetparam
            params["sting"] = boolparser(b.sting)
            params["accumulate"] = boolparser(b.accumulate)
            self._workermanager.instantiate(
                b.wasp_id, workertype, x, y, paramvalues=params
            )

    def load(self, hivemapfile):
        self.clear()

        workermanager = self._workermanager
        localdir = os.path.split(hivemapfile)[0]
        workermanager.find_local_workers(localdir)
        workermanager.build_workers(local=True)

        hivemap = Spyder.Hivemap.fromfile(hivemapfile)
        self._load(hivemap)
        workermanager.sync_antennafoldstate()

    def save(self, hivemapfile, filesaver=None):
        workermanager = self._workermanager
        workers = Spyder.WorkerArray()
        connections = Spyder.WorkerConnectionArray()
        drones = Spyder.DroneArray()
        io = Spyder.HivemapIOArray()
        hparameters = Spyder.HivemapParameterArray()
        hattributes = Spyder.HivemapAttributeArray()
        hpyattributes = Spyder.HivemapPyAttributeArray()
        hparts = Spyder.HivemapPartBeeArray()
        hwasps = Spyder.HivemapWaspArray()
        bees = {}

        # storing workers
        for workerid in sorted(workermanager.workerids()):
            node, mapping = self._wim.get_node(workerid)
            if node.empty: continue
            workertype, params, metaparams = workermanager.get_parameters(workerid)
            if workertype.startswith("bees."):
                bees[workerid] = node, workertype, [], []
                continue
            elif workertype.startswith("<drone>:"):
                droneid = workerid
                dronetype = workertype[len("<drone>:"):]
                parameters = None
                if params is not None:
                    parameters = []
                    for n in range(5):
                        p = params.get("arg%d" % (n + 1), "")
                        parameters.append(p)
                    if parameters == [""] * 5:
                        parameters = None
                    else:
                        pa = Spyder.StringArray()
                        for n in range(5):
                            x = Spyder.String(repr(parameters[n]))
                            pa.append(x)
                        parameters = pa
                d = Spyder.Drone(
                    droneid,
                    dronetype,
                    node.position,
                )
                d.parameters = parameters
                drones.append(d)
                continue
            blockvalues = self._wim.get_blockvalues(workerid)
            if params is not None: params = params.items()
            if metaparams is not None: metaparams = metaparams.items()
            w = Spyder.Worker(
                workerid,
                workertype,
                node.position,
                parameters=params,
                metaparameters=metaparams,
                blockvalues=blockvalues,
            )
            workers.append(w)

        #filtering connections for bees
        nconnections = []
        for c in self._wim.get_connections():
            if c.start_node in bees:
                node, workertype, wcon_in, wcon_out = bees[c.start_node]
                wcon_out.append((c.end_node, c.end_attribute))
            elif c.end_node in bees:
                node, workertype, wcon_in, wcon_out = bees[c.end_node]
                wcon_in.append((c.start_node, c.start_attribute))
            else:
                nconnections.append(c)

        #saving bees
        for bee_id, bee in bees.items():
            node, workertype, wcon_in, wcon_out = bee
            if workertype.startswith("bees.io"):
                if workertype in ("bees.io.push_antenna", "bees.io.pull_antenna"):
                    assert len(wcon_in) == 0  #something wrong with the GUI if this happens
                    if len(wcon_out) == 0:
                        print("Warning: %s '%s' does not have any outgoing connections, bee is not saved!" % (
                        workertype, bee_id))
                        continue
                    elif len(wcon_out) > 1:
                        print("Warning: %s '%s' has multiple outgoing connections, selecting the first..." % (
                        workertype, bee_id))
                    mio = "antenna"
                    hook = "inhook"
                    targetcon = wcon_out[0]
                    mapattr = "_inmapr"
                elif workertype in ("bees.io.push_output", "bees.io.pull_output"):
                    assert len(wcon_out) == 0  #something wrong with the GUI if this happens
                    if len(wcon_in) == 0:
                        print("Warning: %s '%s' does not have any incoming connections, bee is not saved!" % (
                        workertype, bee_id))
                        continue
                    elif len(wcon_in) > 1:
                        print("Warning: %s '%s' has multiple incoming connections, selecting the first..." % (
                        workertype, bee_id))
                    mio = "output"
                    hook = "outhook"
                    targetcon = wcon_in[0]
                    mapattr = "_outmapr"
                else:
                    raise Exception(workertype)
                iomode = workertype[workertype.rindex(".") + 1:workertype.rindex("_")]
                iotype = None
                tnode, targetmapping = self._wim.get_node(targetcon[0])
                for a in tnode.attributes:
                    if a.name == targetcon[1]:
                        iotype = getattr(a, hook).type
                        break
                assert iotype is not None
                targetmap = getattr(targetmapping, mapattr)
                targetio = targetcon[1]
                try:
                    targetio = targetmap[targetio]
                except KeyError:
                    pass
                hio = Spyder.HivemapIO(
                    bee_id,
                    mio,
                    targetcon[0],
                    targetio,
                    iomode,
                    iotype,
                    node.position,
                )
                io.append(hio)
            elif workertype == "bees.attribute":
                params, metaparams = workermanager.get_parameters(bee_id)[1:3]
                if params is None: params = {}
                hatt = Spyder.HivemapAttribute(
                    bee_id,
                    metaparams.get("spydertype", ""),
                    params.get("val", ""),
                    position=node.position
                )
                hattributes.append(hatt)
            elif workertype == "bees.pyattribute":
                params = workermanager.get_parameters(bee_id)[1]
                if params is None: params = {}
                cv = params.get("code_variable", "")
                if cv == "": cv = None
                hpyatt = Spyder.HivemapPyAttribute(
                    bee_id,
                    params.get("code", ""),
                    cv,
                    position=node.position
                )
                hpyattributes.append(hpyatt)
            elif workertype == "bees.parameter":
                params = workermanager.get_parameters(bee_id)[1]
                if params is None: params = {}
                hpar = Spyder.HivemapParameter(
                    bee_id,
                    params.get("internal_name", ""),
                    params.get("typename", ""),
                    position=node.position
                )
                gui_defaultvalue = params.get("gui_defaultvalue", "")
                if gui_defaultvalue != "":
                    hpar.gui_defaultvalue = gui_defaultvalue
                hparameters.append(hpar)
            elif workertype == "bees.part":
                params = workermanager.get_parameters(bee_id)[1]
                if params is None: params = {}
                hpart = Spyder.HivemapPartBee(
                    bee_id,
                    params.get("beename", ""),
                    params.get("part", ""),
                    position=node.position
                )
                hparts.append(hpart)
            elif workertype == "bees.wasp":
                params = workermanager.get_parameters(bee_id)[1]
                if params is None: params = {}
                hwasp = Spyder.HivemapWasp(
                    bee_id,
                    params.get("injected", ""),
                    params.get("target_name", ""),
                    params.get("target_parameter", ""),
                    params.get("sting", False),
                    params.get("accumulate", False),
                    position=node.position
                )
                hwasps.append(hwasp)
            else:
                raise Exception(workertype)

        for c in nconnections:
            start_node, start_mapping = self._wim.get_node(c.start_node)
            end_node, end_mapping = self._wim.get_node(c.end_node)
            try:
                start_attribute = start_mapping._outmapr[c.start_attribute]
            except KeyError:
                start_attribute = c.start_attribute
            try:
                end_attribute = end_mapping._inmapr[c.end_attribute]
            except KeyError:
                end_attribute = c.end_attribute
            con = Spyder.WorkerConnection(
                (c.start_node, start_attribute),
                (c.end_node, end_attribute),
                c.interpoints
            )
            connections.append(con)
        if not len(io): io = None
        if not len(drones): drones = None
        if not len(hparameters): hparameters = None
        if not len(hpyattributes): hpyattributes = None
        if not len(hwasps): hwasps = None
        hivemap = Spyder.Hivemap.empty()
        hivemap.workers = workers
        hivemap.connections = connections
        hivemap.io = io
        hivemap.drones = drones
        hivemap.parameters = hparameters
        hivemap.attributes = hattributes
        hivemap.pyattributes = hpyattributes
        hivemap.partbees = hparts
        hivemap.wasps = hwasps
        #hivemap.tofile(hivemapfile)
        hm = str(hivemap)
        if filesaver:
            filesaver(hivemapfile, hm)
        else:
            open(hivemapfile, "w").write(hm)
        self._lastsave = hivemapfile

    def menu_save_as(self):
        hivemapfile = self._file_dialog("save")
        self.save(hivemapfile)

    def menu_save(self):
        if self._lastsave is None:
            return self.menu_save_as()
        self.save(self._lastsave)

    def menu_refresh(self):
        if self._lastsave is None: return
        self.save(self._lastsave)
        self.load(self._lastsave)

    def menu_load(self):
        hivemapfile = self._file_dialog("open")
        self.load(hivemapfile)
        self._lastsave = hivemapfile

    def clear(self):
        self._workermanager.clear_workers()
        self._workermanager.unbuild_local_workers()
