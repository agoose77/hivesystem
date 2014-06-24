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
            wd.append(workerdesc)

        if wd:
            self._clipboard = "worker_descriptor", wd

    def nodecanvas_copy_nodes(self, nodes):
        self.copy_workers(nodes)

    def paste_workers(self):
        assert self._workermanager is not None
        wm = self._workermanager
        typ, wd = self._clipboard
        if typ != "worker_descriptor": return None

        if len(wd) == 1:
            workerdesc = wd[0]
            workerid, workertype, x, y, metaparamvalues, paramvalues, profile, gp = workerdesc
            if workerid in wm.workerids():
                workerid = wm.get_new_workerid(workerid)
            wm.instantiate(workerid, workertype, x, y, metaparamvalues, paramvalues,
                           self._offset
            )
            if profile != "default":
                wim = wm.get_wim()
                wim.morph_worker(workerid, profile)
            return [workerid]
        else:
            wim = wm.get_wim()
            ret = []

            workermapping = {}
            workers = set()
            wids = wm.workerids()

            for workerdesc in wd:
                workerid, workertype, x, y, metaparamvalues, paramvalues, profile, gp = workerdesc
                workers.add(workerid)
                if workerid in wids:
                    w_old = workerid
                    workerid = wm.get_new_workerid(workerid)
                    workermapping[w_old] = workerid
                wm.instantiate(workerid, workertype, x, y, metaparamvalues, paramvalues,
                               self._offset
                )
                if profile != "default":
                    wim.morph_worker(workerid, profile)
                ret.append(workerid)
            for c in list(wim.get_connections()):
                if c.start_node not in workers: continue
                if c.end_node not in workers: continue
                start = workermapping.get(c.start_node, c.start_node)
                end = workermapping.get(c.end_node, c.end_node)
                con_id = wm.get_new_connection_id("con")
                wim.add_connection(
                    con_id,
                    (start, c.start_attribute),
                    (end, c.end_attribute),
                    c.interpoints,
                )
            if len(ret) == 0: return None
            return ret

    def nodecanvas_paste_nodes(self):
        return self.paste_workers()
