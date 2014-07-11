from __future__ import print_function, absolute_import

from .anyQt import QtGui, QtCore
from .anyQt.QtGui import QTreeWidgetItem


class PTree(object):

    def __init__(self, parent=None, on_select=None):
        self._widget = QtGui.QTreeWidget(parent)
        self._widget.setColumnCount(1)
        self._keys = []
        self._allkeys = set()
        self._allitems = {}
        self._leafitems_rev = {}
        self._widget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self._widget.itemPressed.connect(self._itemPressed)
        self._widget.setDragEnabled(True)
        self._on_select = on_select

    def widget(self):
        return self._widget

    @QtCore.pyqtSlot(QTreeWidgetItem, int)
    def _itemPressed(self, item, column):
        if id(item) in self._leafitems_rev:
            t = self._leafitems_rev[id(item)]
            if self._on_select is not None:
                self._on_select(t)
            self._widget.setDragEnabled(True)
        else:
            self._widget.setDragEnabled(False)

    def append(self, key):
        assert key not in self._keys
        head, tail = key[0], key[1:]
        if head not in self._allkeys:
            self._allkeys.add(head)
            e = QTreeWidgetItem()
            e.setText(0, head)
            self._widget.addTopLevelItem(e)
            self._allitems[head] = e
            w = e
        else:
            w = self._allitems[head]
        t = key[1:]
        prev = (head,)
        while len(t) > 0:
            head, tail = t[0], t[1:]
            phead = prev + (head,)
            if phead not in self._allkeys:
                self._allkeys.add(phead)
                e = QTreeWidgetItem()
                e.setText(0, head)
                w.addChild(e)
                self._allitems[phead] = e
                w = e
            else:
                w = self._allitems[phead]
            t = tail
            prev = phead
        key = tuple(key)
        self._keys.append(key)
        self._leafitems_rev[id(w)] = key

    def _remove_empty_group(self, group):
        g = len(group)
        nr_items = len([k for k in self._allitems.keys() if k[:g] == group])
        min = 1 if g > 1 else 0
        if nr_items == min:
            if len(group) == 1:
                group = group[0]
                self._allkeys.remove(group)
                w = self._allitems.pop(group)
                ind = self._widget.indexOfTopLevelItem(w)
                self._widget.takeTopLevelItem(ind)
            else:
                self._allkeys.remove(group)
                w = self._allitems.pop(group)
                parent = group[:-1]
                if len(parent) == 1: parent = parent[0]
                ww = self._allitems[parent]
                ww.removeChild(w)

    def remove(self, key):
        key = tuple(key)
        assert key in self._keys

        self._keys.remove(key)
        self._allkeys.remove(key)
        w = self._allitems.pop(key)
        self._leafitems_rev.pop(id(w))
        if len(key) == 1:
            ind = self._widget.indexOfTopLevelItem(w)
            self._widget.takeTopLevelItem(ind)
        else:
            parent = key[:-1]
            if len(parent) == 1: parent = parent[0]
            ww = self._allitems[parent]
            ww.removeChild(w)
        for n in range(len(key), 0, -1):
            group = key[:n]
            self._remove_empty_group(group)

    def sync(self):
        pass
