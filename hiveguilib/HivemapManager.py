from __future__ import print_function, absolute_import
from bee.types import boolparser, spyderparser

import os
import spyder, Spyder


class HivemapManager(object):
    """Interface to .hivemap objects"""

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

    def _load(self, hivemap, soft_load=False, pre_load=None):
        worker_id_mapping = {}
        worker_ids = []

        for worker in hivemap.workers:
            x, y = worker.position.x, worker.position.y
            metaparamvalues = None
            if worker.metaparameters is not None:
                metaparamvalues = {}
                for param in worker.metaparameters:
                    metaparamvalues[param.pname] = param.pvalue

            paramvalues = None
            if worker.parameters is not None:
                paramvalues = {}
                for param in worker.parameters:
                    paramvalues[param.pname] = param.pvalue

            worker_manager = self._workermanager
            existing_ids = worker_manager.workerids()
            # If an ID clash occurred
            worker_id = worker.workerid

            if worker_id in existing_ids and soft_load:
                old_worker_id = worker_id
                worker_id = worker_manager.get_new_workerid(worker_id)
                worker_id_mapping[old_worker_id] = worker_id

                if callable(pre_load):
                    pre_load(old_worker_id, worker_id)

            else:
                # The new ID and the previous ID are the same
                if callable(pre_load):
                    pre_load(worker_id, worker_id)

            worker_ids.append(worker_id)

            try:
                self._workermanager.instantiate(worker_id, worker.workertype, x, y, metaparamvalues, paramvalues)

            except KeyError:
                print("Unknown worker:", worker.workertype, worker_id)
                continue

            if worker.blockvalues:
                self._wim.worker_update_blockvalues(worker_id, worker.blockvalues)

        if hivemap.drones is not None:
            for drone in hivemap.drones:
                x, y = drone.position.x, drone.position.y
                parameters = drone.parameters
                try:
                    self._workermanager.create_drone(
                        drone.droneid, drone.dronetype, x, y, parameters
                    )

                except KeyError:
                    print("Unknown drone:", drone.dronetype, drone.droneid)
                    continue

        for connection in hivemap.connections:
            connection_id = self._workermanager.get_new_connection_id("con")
            interpoints = [(ip.x, ip.y) for ip in connection.interpoints]

            start_id = connection.start.workerid
            end_id = connection.end.workerid

            # Support renamed workers for connections
            start_id = worker_id_mapping.get(start_id, start_id)
            end_id = worker_id_mapping.get(end_id, end_id)

            print(start_id, "Connection Start")

            self._wim.add_connection(connection_id, (start_id, connection.start.io),
                                     (end_id, connection.end.io), interpoints)

        hmio = hivemap.io
        if hmio is None:
            hmio = []

        for b in hmio:
            x, y = b.position.x, b.position.y
            target = self._workermanager.get_workertemplate(b.worker)
            if b.io == "Antenna":
                try:
                    mode = target.antennas[b.workerio][0]
                except KeyError:
                    assert target.block is not None
                    assert target.block.io == "Antenna"
                    mode = target.block.mode
                source = (b.io_id, "outp")
                target = (b.worker, b.workerio)
            else:
                try:
                    mode = target.outputs[b.workerio][0]
                except KeyError:
                    assert target.block is not None
                    assert target.block.io == "Output"
                    mode = target.block.mode
                source = (b.worker, b.workerio)
                target = (b.io_id, "inp")
            workertype = "bees.io." + mode + "_" + b.io
            self._workermanager.instantiate(
                b.io_id, workertype, x, y
            )
            connection_id = self._workermanager.get_new_connection_id("con")
            self._wim.add_connection(
                connection_id,
                source,
                target,
            )

        hmpar = hivemap.parameters
        if hmpar is None: hmpar = []
        for b in hmpar:
            x, y = b.position.x, b.position.y
            workertype = "bees.Parameter"
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
        self._workermanager.select(worker_ids)

    def load(self, hivemapfile):
        self.clear()

        worker_manager = self._workermanager
        local_directory = os.path.split(hivemapfile)[0]
        worker_manager.find_local_workers(local_directory)
        worker_manager.build_workers(local=True)

        hivemap = Spyder.Hivemap.fromfile(hivemapfile)
        self._load(hivemap)

    def save(self, hivemapfile, filesaver=None):
        # Default to all worker ids
        worker_ids = self._workermanager.workerids()
        hivemap = self._save(worker_ids)

        # Save to file
        hivemap.validate()
        hivemap_string = str(hivemap)

        if filesaver:
            filesaver(hivemapfile, hivemap_string)
        else:
            open(hivemapfile, "w").write(hivemap_string)

        self._lastsave = hivemapfile

    def _save(self, worker_ids):
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
        for workerid in sorted(worker_ids):
            node, mapping = self._wim.get_node(workerid)
            if node.empty:
                continue

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
                    for index in range(5):
                        parameter = params.get("arg%d" % (index + 1), "")
                        parameters.append(parameter)

                    if not any(parameters):
                        parameters = None

                    else:
                        parameter_array = Spyder.StringArray()
                        for index in range(5):
                            parameter_string = Spyder.String(repr(parameters[index]))
                            parameter_array.append(parameter_string)

                        parameters = parameter_array

                drone = Spyder.Drone(droneid, dronetype, node.position)
                drone.parameters = parameters
                drones.append(drone)
                continue

            blockvalues = self._wim.get_blockvalues(workerid)
            if params is not None:
                params = params.items()

            if metaparams is not None:
                metaparams = metaparams.items()

            worker = Spyder.Worker(workerid, workertype, node.position, parameters=params, metaparameters=metaparams,
                              blockvalues=blockvalues)
            workers.append(worker)

        #filtering connections for bees
        nconnections = []
        for connection in self._wim.get_connections():
            if connection.start_node in bees:
                node, workertype, wcon_in, wcon_out = bees[connection.start_node]
                wcon_out.append((connection.end_node, connection.end_attribute))

            elif connection.end_node in bees:
                node, workertype, wcon_in, wcon_out = bees[connection.end_node]
                wcon_in.append((connection.start_node, connection.start_attribute))

            else:
                nconnections.append(connection)

        #saving bees
        for bee_id, bee in bees.items():
            node, workertype, wcon_in, wcon_out = bee
            if workertype.startswith("bees.io"):
                if workertype in ("bees.io.push_antenna", "bees.io.pull_antenna"):
                    assert not wcon_in  #something wrong with the GUI if this happens
                    if not wcon_out:
                        print("Warning: %s '%s' does not have any outgoing connections, bee is not saved!" % (
                        workertype, bee_id))
                        continue

                    elif len(wcon_out) > 1:
                        print("Warning: %s '%s' has multiple outgoing connections, selecting the first..." % (
                        workertype, bee_id))

                    mio = "Antenna"
                    hook = "inhook"
                    targetcon = wcon_out[0]
                    mapattr = "_inmapr"

                elif workertype in ("bees.io.push_output", "bees.io.pull_output"):
                    assert not wcon_out  #something wrong with the GUI if this happens
                    if not wcon_in:
                        print("Warning: %s '%s' does not have any incoming connections, bee is not saved!" % (
                        workertype, bee_id))
                        continue

                    elif len(wcon_in) > 1:
                        print("Warning: %s '%s' has multiple incoming connections, selecting the first..." % (
                        workertype, bee_id))

                    mio = "Output"
                    hook = "outhook"
                    targetcon = wcon_in[0]
                    mapattr = "_outmapr"

                else:
                    raise Exception(workertype)

                iomode = workertype[workertype.rindex(".") + 1:workertype.rindex("_")]
                iotype = None
                tnode, targetmapping = self._wim.get_node(targetcon[0])
                for attribute in tnode.attributes:
                    if attribute.name == targetcon[1]:
                        iotype = getattr(attribute, hook).type
                        break

                assert iotype is not None
                targetmap = getattr(targetmapping, mapattr)
                targetio = targetcon[1]

                try:
                    targetio = targetmap[targetio]
                except KeyError:
                    pass

                hivemap_io = Spyder.HivemapIO(bee_id, mio, targetcon[0], targetio, iomode, iotype,  node.position)
                io.append(hivemap_io)

            elif workertype == "bees.attribute":
                params, metaparams = workermanager.get_parameters(bee_id)[1:3]
                if params is None:
                    params = {}

                attribute = Spyder.HivemapAttribute(bee_id, metaparams.get("spydertype", ""), params.get("val", ""),
                                                    position=node.position)
                hattributes.append(attribute)

            elif workertype == "bees.pyattribute":
                params = workermanager.get_parameters(bee_id)[1]
                if params is None:
                    params = {}

                code_variable = params.get("code_variable", "")
                if code_variable == "":
                    code_variable = None

                py_attribute = Spyder.HivemapPyAttribute(bee_id, params.get("code", ""), code_variable,
                                                         position=node.position)
                hpyattributes.append(py_attribute)

            elif workertype == "bees.Parameter":
                params = workermanager.get_parameters(bee_id)[1]
                if params is None:
                    params = {}

                hpar = Spyder.HivemapParameter(bee_id, params.get("internal_name", ""), params.get("typename", ""),
                                               position=node.position)

                gui_defaultvalue = params.get("gui_defaultvalue", "")
                if gui_defaultvalue != "":
                    hpar.gui_defaultvalue = gui_defaultvalue

                hparameters.append(hpar)

            elif workertype == "bees.part":
                params = workermanager.get_parameters(bee_id)[1]
                if params is None:
                    params = {}

                hpart = Spyder.HivemapPartBee(bee_id, params.get("beename", ""), params.get("part", ""),
                                              position=node.position)
                hparts.append(hpart)

            elif workertype == "bees.wasp":
                params = workermanager.get_parameters(bee_id)[1]
                if params is None:
                    params = {}

                hwasp = Spyder.HivemapWasp(bee_id, params.get("injected", ""), params.get("target_name", ""),
                    params.get("target_parameter", ""), params.get("sting", False), params.get("accumulate", False),
                    position=node.position
                )
                hwasps.append(hwasp)

            else:
                raise Exception(workertype)

        for connection in nconnections:
            start_node, start_mapping = self._wim.get_node(connection.start_node)
            end_node, end_mapping = self._wim.get_node(connection.end_node)

            # Only save wanted connections
            if not (connection.start_node in worker_ids and connection.end_node in worker_ids):
                continue

            try:
                start_attribute = start_mapping._outmapr[connection.start_attribute]
            except KeyError:
                start_attribute = connection.start_attribute

            try:
                end_attribute = end_mapping._inmapr[connection.end_attribute]
            except KeyError:
                end_attribute = connection.end_attribute

            connection = Spyder.WorkerConnection((connection.start_node, start_attribute),
                                                 (connection.end_node, end_attribute), connection.interpoints)
            connections.append(connection)

        if not io:
            io = None

        if not drones:
            drones = None

        if not hparameters:
            hparameters = None

        if not hpyattributes:
            hpyattributes = None

        if not hwasps:
            hwasps = None

        hivemap = Spyder.Hivemap.empty()
        hivemap.workers = workers
        hivemap.connections = connections
        hivemap.io = io
        hivemap.drones = drones
        hivemap.parameters = hparameters
        hivemap.attributes = hattributes
        hivemap.pyattributes = hpyattributes
        hivemap.docstring = "TEST"
        hivemap.partbees = hparts
        hivemap.wasps = hwasps
        #hivemap.tofile(hivemapfile)

        return hivemap

    def menu_save_as(self):
        hivemapfile = self._file_dialog("save")
        self.save(hivemapfile)

    def menu_save(self):
        if self._lastsave is None:
            return self.menu_save_as()

        self.save(self._lastsave)

    def menu_refresh(self):
        if self._lastsave is None:
            return

        self.save(self._lastsave)
        self.load(self._lastsave)

    def menu_load(self):
        hivemapfile = self._file_dialog("open")
        self.load(hivemapfile)
        self._lastsave = hivemapfile

    def clear(self):
        self._workermanager.clear_workers()
        self._workermanager.unbuild_local_workers()
