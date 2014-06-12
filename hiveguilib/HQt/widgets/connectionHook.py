# <license>
# Copyright (C) 2011 Andrea Interguglielmi, All rights reserved.
# This file is part of the coral repository downloaded from http://code.google.com/p/coral-repo.
# 
# Modified for the Hive system by Sjoerd de Vries
# All modifications copyright (C) 2012 Sjoerd de Vries, All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
# 
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# </license>

from __future__ import print_function, absolute_import

import copy
import weakref
from ..anyQt import QtGui, QtCore

#from ... import coralApp
#from ..._coral import ErrorObject
#from . import nodeView

class ConnectionHook(QtGui.QGraphicsItem):
    def __init__(self,
                 parentAttributeUi, mode, shape, style,
                 parentItem=None, hoverText=None, orderDependent=False
    ):
        if parentItem is None:  # parentItem is used by builtinUis.ContainedAttributeUiProxy
            parentItem = parentAttributeUi

        QtGui.QGraphicsItem.__init__(self, parentItem)

        self._parentNodeUi = weakref.ref(parentAttributeUi.parentNodeUi())
        self._parentAttributeUi = weakref.ref(parentAttributeUi)
        assert mode in ("input", "output"), mode
        self._mode = mode
        assert shape in ("circle", "square"), shape
        self._shape = shape
        assert style in ("dot", "dashed", "solid"), style
        self._style = style
        self._rect = QtCore.QRectF(0, 0, 12, 12)
        self._color = QtGui.QColor(200, 200, 200)
        self._brush = QtGui.QBrush(self.color())
        self._pen = QtGui.QPen(QtCore.Qt.NoPen)
        self._draggingConnection = None
        self._draggingConnectionEndHook = None
        self._connections = []
        self._hoverText = hoverText
        self._orderDependent = orderDependent

        self._mixedColor = False

        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges, True)

        self._pen.setWidthF(1.0)

        self.setAcceptsHoverEvents(True)

        self._selectedConnection = None

    """
    def reparent(self, parentAttributeUi):        
        self._parentNodeUi = weakref.ref(parentAttributeUi.parentNodeUi())
        self._parentAttributeUi = weakref.ref(parentAttributeUi)
        pos = self.scenePos()
        self.setParentItem(parentAttributeUi)
        self.setPos(self.mapFromScene(pos))
    """

    def _tabKey(self):
        self._selectNextConnection()

    def _bspKey(self):
        self._selectPrevConnection()

    def _deleteKey(self):
        l = len(self._connections)
        if l == 0: return
        sel = self._selectedConnection
        if sel is None:
            if l == 1:
                nr = 0
            else:
                return
        else:
            nr = self._selectedConnection
        inputConnection = self._connections[nr]

        canvas = self._parentNodeUi().scene()._hqt
        if canvas:
            ok = canvas().gui_removes_connection(inputConnection)
            if not ok:
                return
        self.parentAttributeUi().parentNodeUi().update()
        inputConnection.deleteIt()
        self._selectConnection(None)

    def _plusKey(self):
        if not self._orderDependent: return
        if self._selectedConnection is None: return
        old_pos = self._selectedConnection
        new_pos = old_pos + 1
        if new_pos == len(self._connections): new_pos = 0
        self._rearrange_connection(old_pos, new_pos)

    def _minusKey(self):
        if not self._orderDependent: return
        if self._selectedConnection is None: return
        old_pos = self._selectedConnection
        new_pos = old_pos - 1
        if new_pos == -1: new_pos = len(self._connections) - 1
        self._rearrange_connection(old_pos, new_pos)

    def _numKey(self, num):
        if not self._orderDependent: return
        if self._selectedConnection is None: return
        old_pos = self._selectedConnection
        new_pos = num - 1
        if new_pos >= len(self._connections):
            new_pos = len(self._connections) - 1
        self._rearrange_connection(old_pos, new_pos)

    def _rearrange_connection(self, old_pos, new_pos):
        connection = self._connections[old_pos]
        mode = "before"
        new_pos2 = new_pos + 1
        if new_pos2 == len(self._connections):
            new_pos2 = new_pos
            mode = "after"
        other_connection = self._connections[new_pos2]
        ok = True
        canvas = self._parentNodeUi().scene()._hqt
        if canvas:
            ok = canvas().gui_rearranges_connection(
                connection, other_connection, mode
            )
        if not ok: return

        sel_con = self._connections[self._selectedConnection]
        connection = self._connections.pop(old_pos)
        if new_pos == len(self._connections):
            self._connections.append(connection)
        else:
            self._connections.insert(new_pos, connection)
        self._selectedConnection = self._connections.index(sel_con)
        for con in self._connections: con.updatePath()

    def _selectNextConnection(self):
        l = len(self._connections)
        if l <= 1: return
        if self._selectedConnection is None:
            nr = 0
        else:
            nr = self._selectedConnection + 1
            if nr == l: nr = 0
        self._selectConnection(nr)

    def _selectPrevConnection(self):
        l = len(self._connections)
        if l <= 1: return
        if self._selectedConnection is None:
            nr = l - 1
        else:
            nr = self._selectedConnection - 1
            if nr == -1: nr = l - 1
        self._selectConnection(nr)

    def _selectConnection(self, nr):
        if nr is None:
            if self._selectedConnection is None: return
            for cnr, conn in enumerate(self.connections()):
                conn.setSelected(False)
                conn.setActive(True)
                conn.update()
        else:
            for cnr, conn in enumerate(self.connections()):
                conn.setSelected(cnr == nr)
                conn.update()
        self._selectedConnection = nr

    def isInput(self):
        return self._mode == "input"

    def isOutput(self):
        return self._mode == "output"

    def connections(self):
        return self._connections

    def hoverEnterEvent(self, event):
        self.scene().setFocusedHook(self)
        self._selectedConnection = None
        for conn in self.connections():
            conn.setActive(True)
            conn.update()
        canvas = self._parentNodeUi().scene()._hqt
        if canvas:
            if self._hoverText is None:
                canvas().clear_statusbar_message()
            else:
                canvas().set_statusbar_message(self._hoverText)


    def hoverLeaveEvent(self, event):
        self.scene().setFocusedHook(None)
        for conn in self.connections():
            conn.setActive(False)
            conn.update()
        canvas = self._parentNodeUi().scene()._hqt
        if canvas:
            canvas().clear_statusbar_message()

    def setMixedColor(self, value=True):
        self._mixedColor = value

    def setBorderEnabled(self, value=True):
        if value:
            self._pen.setStyle(QtCore.Qt.SolidLine)
        else:
            self._pen.setStyle(QtCore.Qt.NoPen)

    def updateToolTip(self):
        tooltip = self._parentAttributeUi().toolTip()
        if tooltip is None: tooltip = ""
        self.setToolTip(tooltip)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemScenePositionHasChanged:
            self.updateWorldPos()

        return value

    def updateWorldPos(self):
        if self._mode == "input":
            for conn in self._connections:
                conn.updateEndPos()
        else:
            for conn in self._connections:
                conn.updateStartPos()

    def addConnection(self, connection):
        self._selectConnection(None)
        assert connection not in self._connections
        self._connections.append(connection)
        for con in self._connections: con.updatePath()

    def connectionIndex(self, connection):
        return self._connections.index(connection), len(self._connections)

    def removeConnection(self, connection):
        self._selectConnection(None)
        self._connections.remove(connection)
        for con in self._connections: con.updatePath()

    def parentAttributeUi(self):
        return self._parentAttributeUi()

    def parentNodeUi(self):
        return self._parentNodeUi()

    def setColor(self, color):
        self._color.setRgb(color.red(), color.green(), color.blue())
        self._brush.setColor(self._color)
        self._pen.setColor(self._color.darker(150))

    def color(self):
        return QtGui.QColor(self._color)

    def mixedColor(self):
        return self._mixedColor

    def setColorRef(self, color):
        self._color = color

    def colorRef(self):
        return self._color

    def mousePressEvent(self, event):
        from . import Connection

        if self._draggingConnection:
            if event.button() == QtCore.Qt.RightButton:
                mousePos = self._draggingConnection.mapFromScene(event.scenePos())
                self._draggingConnection.insertInterpoint(None, mousePos)
            event.accept()
            return

        if event.button() == QtCore.Qt.RightButton:
            event.ignore()
            return

        if self._mode == "output":
            self._selectConnection(None)
            self._draggingConnection = Connection(self)
            self._draggingConnection.setActive(False)

        elif self._mode == "input" and len(self._connections):
            con_index = -1
            if self._selectedConnection is not None:
                con_index = self._selectedConnection
            inputConnection = self._connections[con_index]

            canvas = self._parentNodeUi().scene()._hqt
            if canvas:
                ok = canvas().gui_removes_connection(inputConnection)
                if not ok:
                    event.accept()
                    return
            self.parentAttributeUi().parentNodeUi().update()

            outHook = inputConnection.startHook()
            inputConnection.deleteIt()

            self._draggingConnection = Connection(outHook)
            self._draggingConnection.setActive(False)

            mousePos = self._draggingConnection.mapFromScene(event.scenePos())
            self._draggingConnection.endHook().setPos(mousePos)
            self._draggingConnection.updatePath()

    def _handleHover(self, item):
        nodeHovered = None

        collidingItems = item.collidingItems(QtCore.Qt.IntersectsItemBoundingRect)
        if collidingItems:
            nodeHovered = collidingItems[0]

        if nodeHovered:
            nodeHovered.hoverEnterEvent(None)
            #elif nodeView.NodeView._lastHoveredItem:
            #    nodeView.NodeView._lastHoveredItem.hoverLeaveEvent(None)

    def mouseMoveEvent(self, event):
        if self._draggingConnection:
            mousePos = self._draggingConnection.mapFromScene(event.scenePos())
            self.drag(mousePos)

    def drag(self, mousePos):
        connectionStartHook = self._draggingConnection.startHook()
        self._draggingConnection.setColor(connectionStartHook.color())

        connectionEndHook = self._draggingConnection.endHook()

        connectionEndHook.setPos(mousePos)

        self._handleHover(self._draggingConnection.endHook())

        endHook = self._draggingConnection.findClosestHook()
        self._draggingConnection.setActive(False)

        if endHook:
            ok = True
            canvas = self._parentNodeUi().scene()._hqt
            if canvas is not None:
                ok = canvas().gui_asks_connection(self._draggingConnection, endHook)
            if ok:
                self._draggingConnection.setActive(True)
                hookSize = endHook.boundingRect().bottomRight() / 2.0
                hookPos = self._draggingConnection.mapFromItem(endHook, hookSize.x(), hookSize.y())
                connectionEndHook.setPos(hookPos)
            else:
                self._draggingConnection.setActive(False)

        else:
            #TODO
            if QtGui.QToolTip.isVisible():
                QtGui.QToolTip.hideText()

        self._draggingConnection.updateEndPos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self._draggingConnection:
                endHook = self._draggingConnection.findClosestHook()
                if endHook:
                    dummyEndHook = self._draggingConnection.endHook()
                    self._draggingConnection.setEndHook(endHook)
                    if dummyEndHook is not None and dummyEndHook is not endHook:
                        self.scene().removeItem(dummyEndHook)
                    hookSize = endHook.boundingRect().bottomRight() / 2.0
                    hookPos = self._draggingConnection.mapFromItem(endHook, hookSize.x(), hookSize.y())
                    self._draggingConnection.setActive(True)
                    self._draggingConnection._isTempConnection = False
                    draggingConnection = self._draggingConnection
                    self._draggingConnection = None

                    canvas = self._parentNodeUi().scene()._hqt
                    force = False
                    if event.modifiers() == QtCore.Qt.ControlModifier:
                        force = True
                    if canvas:
                        ok = canvas().gui_adds_connection(draggingConnection, force)
                        if not ok:
                            if not force:
                                draggingConnection.deleteIt()
                    self.parentAttributeUi().parentNodeUi().update()
                else:
                    self._cancelDraggingConnection()

    def _cancelDraggingConnection(self):
        startHook = self._draggingConnection.startHook()
        self._draggingConnection.deleteIt()
        self._draggingConnection = None

        if self._draggingConnectionEndHook:
            self._draggingConnectionEndHook = None
            self.parentAttributeUi().parentNodeUi().update()

    def boundingRect(self):
        return self._rect

    def paint(self, painter, option, widget):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        if self._shape == "circle":
            painter.drawEllipse(self._rect)
        elif self._shape == "square":
            painter.save()
            c = self._rect.center()
            painter.translate(c)
            painter.rotate(45)
            painter.scale(0.8, 0.8)
            painter.drawRect(self._rect.translated(-c))
            painter.restore()
        else:
            raise ValueError(self._shape)

        if self._mixedColor:
            painter.setBrush(painter.brush().color().darker(130))
            painter.drawChord(self._rect, 1 * 16, 180 * 16)

    def deleteIt(self):
        conns = list(self.connections())
        for conn in conns:
            conn.deleteIt()
