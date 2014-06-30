from __future__ import print_function, absolute_import


class Clipboard(object):
    def __init__(self):
        self._workermanager = None
        self._dragboard = None, None
        self._clipboard = None, None
        self._offset = (30, -30)

    def set_workermanager(self, workermanager):
        self._workermanager = workermanager

    def set_dragboard_value(self, typ, name):
        self._dragboard = (typ, name)

    def set_clipboard_value(self, typ, name):
        self._clipboard = (typ, name)

    def get_clipboard_value(self):
        return self._clipboard

    def drop_worker(self, x, y):
        assert self._workermanager is not None
        typ, name = self._dragboard
        if typ == "worker":
            id_ = self._workermanager.get_new_workerid(name)
            id_ = self._workermanager.create(id_, name, x, y)
            self._workermanager.select([id_])
            self._dragboard = None, None
            return True
        elif typ == "spydermap":
            id_ = self._workermanager.get_new_workerid(name)
            id_ = self._workermanager.create_spydermap(id_, name, x, y)
            self._workermanager.select([id_])
            self._dragboard = None, None
            return True
        elif typ == "drone":
            id_ = self._workermanager.get_new_workerid(name)
            id_ = self._workermanager.create_drone(id_, name, x, y)
            self._workermanager.select([id_])
            self._dragboard = None, None
            return True
        else:
            return False

    def copy_workers(self, workerids):
        assert self._workermanager is not None
        wm = self._workermanager
        wd = []

        for workerid in workerids:
            workerdesc = wm.get_worker_descriptor(workerid)

            if workerdesc is None:
                continue

            worker_connections = wm.get_worker_connections(workerid)
            worker_expanded_antennas = wm.get_expanded_antennas(workerid)
            wd.append((workerdesc, worker_connections, worker_expanded_antennas))

        if wd:
            self._clipboard = "worker_descriptor", wd

    def nodecanvas_copy_nodes(self, nodes):
        self.copy_workers(nodes)

    def paste_workers(self, pre_conversion=None):
        assert self._workermanager is not None
        wm = self._workermanager
        worker_type, worker_description = self._clipboard

        if worker_type != "worker_descriptor":
            return None

        worker_id_mapping = {}
        wim = wm.get_wim()
        new_worker_ids = []

        workers = set()
        wids = wm.workerids()

        for workerdesc, worker_connections, worker_expanded_antennas in worker_description:
            workerid, workertype, x, y, metaparamvalues, paramvalues, profile, gp = workerdesc
            workers.add(workerid)

            if workerid in wids:
                old_worker_id = workerid
                workerid = wm.get_new_workerid(workerid)
                worker_id_mapping[old_worker_id] = workerid

                if callable(pre_conversion):
                    pre_conversion(old_worker_id, workerid)

            else:
                # The new ID and the previous ID are the same
                if callable(pre_conversion):
                    pre_conversion(workerid, workerid)

            wm.instantiate(workerid, workertype, x, y, metaparamvalues, paramvalues, self._offset)

            # Initial expansion of variables
            for expanded_antenna_name in worker_expanded_antennas:
                wm._antennafoldstate.expand(workerid, expanded_antenna_name)

            if profile != "default":
                wim.morph_worker(workerid, profile)
            new_worker_ids.append(workerid)

            # Restore old connections
            for connection in worker_connections:
                start = worker_id_mapping.get(connection.start_node, connection.start_node)
                end = worker_id_mapping.get(connection.end_node, connection.end_node)
                con_id = wm.get_new_connection_id("con")
                # TODO handle this properly
                try:
                    wim.add_connection(con_id, (start, connection.start_attribute), (end, connection.end_attribute),
                                       connection.interpoints)
                except KeyError as e:
                    print("CANNOT CONNECT", e, start, end)
                    raise
                    continue

        # # Expand variables
        # for workerdesc, worker_connections, worker_expanded_antennas in worker_description:
        #     worker_id, workertype, x, y, metaparamvalues, paramvalues, profile, gp = workerdesc
        #     worker_id = worker_id_mapping.get(worker_id, worker_id)
        #
        #     # TODO REMOVE HACK
        #     for expanded_antenna_name in worker_expanded_antennas:
        #         wm._antennafoldstate.expand(workerid, expanded_antenna_name)

        if not new_worker_ids:
            return None

        return new_worker_ids

    def nodecanvas_paste_nodes(self, pre_conversion=None):
        return self.paste_workers(pre_conversion)
