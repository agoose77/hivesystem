import logging


class PTree(object):

    def __init__(self, parent=None, on_select=None):
        # In Blender, we are not really an independent widget;
        # instead, we re-direct all operations to the Blender NodeItemManager
        self._nodeitemmanager = None
        self._nodetreename = None

    def set_nodetreename(self, nodetreename):
        self._nodetreename = nodetreename

    def set_nodeitemmanager(self, nodeitemmanager):
        self._nodeitemmanager = nodeitemmanager

    def append(self, key):
        assert self._nodeitemmanager is not None
        assert self._nodetreename is not None
        self._nodeitemmanager.append(self._nodetreename, key)

    def remove(self, key):
        assert self._nodeitemmanager is not None
        assert self._nodetreename is not None
        self._nodeitemmanager.remove(self._nodetreename, key)

    def widget(self):
        # logging.debug("PTree.widget, what to do?")
        return self
    
    