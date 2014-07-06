from __future__ import print_function, absolute_import

import weakref


class PWorkerCreator(object):

    def __init__(self, mainwindow, clipboard, title="workers"):
        self._mainwindow = mainwindow
        self._clipboard = clipboard
        self._subwin = mainwindow.newSubWindow(title)
        from . import PTree

        self._tree = PTree(self._subwin.wrapwidget(), self._select_worker)
        self._subwin.setWidget(self._tree.widget())
        self._hivemapworkers = {}
        self._hivemapworkers_rev = {}
        self._spydermapworkers = {}
        self._spydermapworkers_rev = {}

    def _select_worker(self, workertype0):
        if workertype0 in self._spydermapworkers:
            workertype = self._spydermapworkers[workertype0]
            self._clipboard.set_dragboard_value("spydermap", workertype)
            return
        if workertype0 in self._hivemapworkers:
            workertype = self._hivemapworkers[workertype0]
        else:
            workertype = ".".join(workertype0)
        self._clipboard.set_dragboard_value("worker", workertype)

    def append(self, workername):
        if workername.find(":") > -1:  # hivemapworker
            key0, key1 = workername.split(":")
            key0a = key0.split(".")
            key1a, _ = key1.split(".")
            key = tuple(key0a) + (key1a,)
            self._hivemapworkers[key] = workername
            self._hivemapworkers_rev[workername] = key

        elif workername.find("#") > -1:  # spydermapworker
            key0, key1 = workername.split("#")
            key0a = key0.split(".")
            key1a, _ = key1.split(".")
            key = tuple(key0a) + (key1a,)
            self._spydermapworkers[key] = workername
            self._spydermapworkers_rev[workername] = key

        else:
            key = tuple(workername.split("."))

        self._tree.append(key)

    def remove(self, workername):
        if workername in self._hivemapworkers_rev:
            key = self._hivemapworkers_rev.pop(workername)
            self._hivemapworkers.pop(key)

        elif workername in self._spydermapworkers_rev:
            key = self._spydermapworkers_rev.pop(workername)
            self._spydermapworkers.pop(key)

        else:
            key = tuple(workername.split("."))

        self._tree.remove(key)
