from __future__ import print_function, absolute_import

import weakref


class PDroneCreator(object):
    def __init__(self, mainwindow, clipboard, title="drones"):
        self._mainwindow = mainwindow
        self._clipboard = clipboard
        self._subwin = mainwindow.newSubWindow(title)
        from . import PTree

        self._tree = PTree(self._subwin.wrapwidget(), self._select_drone)
        self._subwin.setWidget(self._tree.widget())

    def _select_drone(self, dronetype):
        dronetype = ".".join(dronetype)
        self._clipboard.set_dragboard_value("drone", dronetype)

    def append(self, dronename):
        key = tuple(dronename.split("."))
        self._tree.append(key)

    def remove(self, dronename):
        key = tuple(dronename.split("."))
        self._tree.remove(key)
