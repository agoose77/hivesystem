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
        print("Clipboard:")
        for workerid in workerids:
            workerdesc = wm.get_worker_descriptor(workerid)

            if workerdesc is None:
                continue
            print(workerid)
            wd.append(workerdesc)

        if wd:
            self._clipboard = "worker_descriptor", wd
        print("\n\n\n\n")

    def nodecanvas_copy_nodes(self, nodes):
        self.copy_workers(nodes)

    def paste_workers(self):
        assert self._workermanager is not None
        wm = self._workermanager
        worker_type, worker_description = self._clipboard

        if worker_type != "worker_descriptor":
            return None

        worker_id_mapping = {}

        if len(worker_description) == 1:
            workerdesc = worker_description[0]
            workerid, workertype, x, y, metaparamvalues, paramvalues, profile, gp = workerdesc
            if workerid in wm.workerids():
                    old_worker_id = workerid
                    workerid = wm.get_new_workerid(workerid)
                    worker_id_mapping[old_worker_id] = workerid
            wm.instantiate(workerid, workertype, x, y, metaparamvalues, paramvalues, self._offset)

            if profile != "default":
                wim = wm.get_wim()
                wim.morph_worker(workerid, profile)
            return [workerid], worker_id_mapping

        else:
            wim = wm.get_wim()
            new_worker_ids = []

            workers = set()
            wids = wm.workerids()

            for workerdesc in worker_description:
                workerid, workertype, x, y, metaparamvalues, paramvalues, profile, gp = workerdesc
                workers.add(workerid)

                if workerid in wids:
                    old_worker_id = workerid
                    workerid = wm.get_new_workerid(workerid)
                    worker_id_mapping[old_worker_id] = workerid

                wm.instantiate(workerid, workertype, x, y, metaparamvalues, paramvalues, self._offset)
                if profile != "default":
                    wim.morph_worker(workerid, profile)
                new_worker_ids.append(workerid)

            for connection in list(wim.get_connections()):
                if connection.start_node not in workers:
                    continue
                if connection.end_node not in workers:
                    continue

                start = worker_id_mapping.get(connection.start_node, connection.start_node)
                end = worker_id_mapping.get(connection.end_node, connection.end_node)
                con_id = wm.get_new_connection_id("con")

                wim.add_connection(con_id, (start, connection.start_attribute), (end, connection.end_attribute),
                                   connection.interpoints)
            if not new_worker_ids:
                return None

            return new_worker_ids, worker_id_mapping

    def nodecanvas_paste_nodes(self):
        return self.paste_workers()
