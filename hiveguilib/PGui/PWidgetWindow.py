from __future__ import print_function, absolute_import

import weakref


class PWidgetWindow(object):
    def __init__(self, mainwindow, subwindowname):
        self.subwindowname = subwindowname
        self._mainwindow = mainwindow
        self._subwin = mainwindow.newSubWindow(subwindowname)
        self._emptywidget = mainwindow.h().emptyWidget()
        self._widget = None
        self._pmanager = None

    def setPManager(self, pmanager):
        self._pmanager = weakref.ref(pmanager)

    def pmanager(self):
        if self._pmanager is None: return None
        return self._pmanager()

    def deselect(self):
        self._widget = None
        self._subwin.setWidget(self._emptywidget)
        self._subwin.hide()

    def setWidget(self, widget):
        self._widget = weakref.ref(widget)
        self._subwin.setWidget(widget)
        self._subwin.show()

