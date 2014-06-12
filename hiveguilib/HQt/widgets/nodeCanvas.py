from __future__ import print_function, absolute_import
from ..anyQt import QtGui, QtCore

import weakref


class NodeCanvas(QtGui.QWidget):
    _nodeView = None
    _hqt = None

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self._mainLayout = QtGui.QVBoxLayout(self)

        self.setWindowTitle("node canvas")
        self.setLayout(self._mainLayout)
        self.setContentsMargins(5, 5, 5, 5)

        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        self._mainLayout.setSpacing(5)

    def setNodeView(self, nodeView):
        assert self._nodeView is None
        self._nodeView = nodeView
        self._mainLayout.addWidget(self._nodeView)

    def nodeView(self):
        return self._nodeView

    """ ###
    @staticmethod
    def _setSelection(nodes = [], attributes = [], updateSelected = True):
        pass
        if updateSelected:
            for nodeId in NodeCanvas._selectedNodesId:
                nodeUi = NodeCanvas.findNodeUi(nodeId)
                if nodeUi:
                    nodeUi.setSelected(False)

            for attrId in NodeCanvas._selectedAttributesId:
                attrUi = NodeCanvas.findAttributeUi(attrId)
                if attrUi:
                    attrUi.proxy().setSelected(False)

        nodeSelUpdated = NodeCanvas._setSelectedNodes(nodes)
        attrSelUpdated = NodeCanvas._setSelectedAttributes(attributes)

        if nodeSelUpdated or attrSelUpdated:
            NodeCanvas._notifySelectedNodesChangedObservers()

            if updateSelected:
                for node in nodes:
                    nodeUi = NodeCanvas.findNodeUi(node.id())
                    if nodeUi:
                        nodeUi.setSelected(True)

                for attr in attributes:
                    attrUi = NodeCanvas.findAttributeUi(attr.id())
                    if attrUi:
                        attrUi.proxy().setSelected(True)

    """
