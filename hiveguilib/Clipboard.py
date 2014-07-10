from __future__ import print_function, absolute_import
from functools import wraps

class Clipboard(object):

    def __init__(self):
        self._workermanager = None
        self._mapmanager = None
        self._dragboard = None, None
        self._clipboard = None
        self._offset = (30, -30)

    def set_workermanager(self, workermanager):
        self._workermanager = workermanager

    def set_mapmanager(self, hivemapmanager):
        self._mapmanager = hivemapmanager

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

        elif typ == "spydermap":
            id_ = self._workermanager.get_new_workerid(name)
            id_ = self._workermanager.create_spydermap(id_, name, x, y)

        elif typ == "drone":
            id_ = self._workermanager.get_new_workerid(name)
            id_ = self._workermanager.create_drone(id_, name, x, y)

        else:
            return False

        self._workermanager.select([id_])
        self._dragboard = None, None

        return True

    def copy_workers(self, worker_ids):
        self._clipboard = self._mapmanager._save(worker_ids)

    def nodecanvas_copy_nodes(self, nodes):
        self.copy_workers(nodes)

    def paste_workers(self, pre_load=None):
        assert self._workermanager is not None
        assert self._mapmanager is not None

        worker_ids = []

        @wraps(pre_load)
        def load_wrapper(source_id, new_id):
            worker_ids.append(new_id)
            if callable(pre_load):
                pre_load(source_id, new_id)

        self._mapmanager._load(self._clipboard, soft_load=True, pre_load=load_wrapper)

        return worker_ids

    def nodecanvas_paste_nodes(self, pre_conversion=None):
        return self.paste_workers(pre_conversion)
