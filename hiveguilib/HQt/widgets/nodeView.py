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
#    * Redistributions of source code must retain the above copyright
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

from ..anyQt import QtGui, QtCore

import weakref, functools

class NodeView(QtGui.QGraphicsView):
    _lastHoveredItem = None
    _animSpeed = 50.0
    _animSteps = 50.0
    _panning = False
    
    def __init__(self, parent, clipboard):
        QtGui.QGraphicsView.__init__(self, parent)
        parent.setNodeView(self)
        self._clipboard = clipboard
        
        self._zoom = 1.0
        self._panning = False
        self._currentCenterPoint = QtCore.QPointF()
        self._lastPanPoint = QtCore.QPoint()
        
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setAcceptDrops(True)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setSceneRect(-5000, -5000, 10000, 10000)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        QtGui.QShortcut(QtGui.QKeySequence("Delete"), self, self._deleteKey)
        QtGui.QShortcut(QtGui.QKeySequence("Backspace"), self, self._bspKey)
        QtGui.QShortcut(QtGui.QKeySequence("Tab"), self, self._tabKey)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+C"), self, self._copyKey)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+V"), self, self._pasteKey)
        QtGui.QShortcut(QtGui.QKeySequence("+"), self, self._plusKey)
        QtGui.QShortcut(QtGui.QKeySequence("-"), self, self._minusKey)
        for num in range(1, 10):
          func = functools.partial(self._numKey, num)
          QtGui.QShortcut(QtGui.QKeySequence(str(num)), self, func)
            
    def _bspKey(self):
        if self.scene()._focusedHook is not None: 
            self.scene()._focusedHook._bspKey()
        else: self._deleteKey()

    def _tabKey(self):
        if self.scene()._focusedHook is not None: 
            self.scene()._focusedHook._tabKey()
    def _plusKey(self):
        if self.scene()._focusedHook is not None: 
            self.scene()._focusedHook._plusKey()
        else: self.zoomIn()
    def _minusKey(self):
        if self.scene()._focusedHook is not None: 
            self.scene()._focusedHook._minusKey()
        else: self.zoomOut()
    def _numKey(self, num):
        if self.scene()._focusedHook is not None: 
            self.scene()._focusedHook._numKey(num)
    
    def _copyKey(self):
        nodes = self._selectedNodes()
        if not len(nodes): return
        canvas = self.scene()._hqt
        
        if canvas is not None:
            canvas().copy_clipboard(nodes)
        
    
    def _pasteKey(self):
        canvas = self.scene()._hqt
        
        if canvas is not None:
            canvas().paste_clipboard()
        
    def _deleteKey(self):
        if self.scene()._focusedHook is not None: 
            self.scene()._focusedHook._deleteKey()
            return
        
        nodes = self._selectedNodes()
        if not len(nodes): return
        canvas = self.scene()._hqt
        ok = True
        if canvas is not None:
            ok = canvas().gui_removes_nodes(nodes)
        if not ok: return
        for node in nodes:
            node.deleteIt()    
    
    def setScene(self, newScene):
        QtGui.QGraphicsView.setScene(self, newScene)
        
        self.setZoom(newScene.zoom())

        newCenter = newScene.centerPos()
        self.centerOn(newCenter)
        self._currentCenterPoint = newCenter
        
        newScene.clearSelection()

        if newScene._firstTimeEntering:
            self.frameSceneContent()
            newScene._firstTimeEntering = False
            
    def frameSceneContent(self):
        self.scene().setCenterPos(self.scene().itemsBoundingRect().center())
        newCenter = self.scene().centerPos()
        self.centerOn(newCenter)
        self._currentCenterPoint = newCenter
        
    def dragMoveEvent(self, event):
        event.accept()
    
    def dropEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        if self._clipboard.drop_worker(scenePos.x(), -scenePos.y()):   
          event.accept() 
        else:
          event.ignore()

    def setSelectedItems(self, items):
        self.scene().clearSelection()
        for item in items:
          item.setSelected(True)
            
    def getCenter(self):
        return self._currentCenterPoint
    
    def setCenter(self, centerPoint):
        self._currentCenterPoint = centerPoint
        self.scene().setCenterPos(centerPoint)
        self.centerOn(self._currentCenterPoint);
        
    def mousePressEvent(self, mouseEvent):        
        if mouseEvent.modifiers() == QtCore.Qt.ShiftModifier:
            self._lastPanPoint = mouseEvent.pos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self._panning = True
            NodeView._panning = True
        else:
            QtGui.QGraphicsView.mousePressEvent(self, mouseEvent)
    
    def mouseMoveEvent(self, mouseEvent):
        if self._panning:
            delta = self.mapToScene(self._lastPanPoint) - self.mapToScene(mouseEvent.pos())
            self._lastPanPoint = mouseEvent.pos()
            
            self.setCenter(self.getCenter() + delta)
        else:
            QtGui.QGraphicsView.mouseMoveEvent(self, mouseEvent)
    
    def mouseReleaseEvent(self, mouseEvent):
        if self._panning:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._lastPanPoint = QtCore.QPoint()
            self._panning = False
            NodeView._panning = False
        else:
            QtGui.QGraphicsView.mouseReleaseEvent(self, mouseEvent)
    
    def wheelEvent(self, event):
        if event.orientation() == QtCore.Qt.Vertical:
            delta = event.delta()
            zoom = self._zoom
            if delta > 0:
                zoom += 0.05
            else:
                zoom -= 0.05
            
            self.setZoom(zoom)
    
    def _selectedNodes(self):
        from . import NodeUi
        nodes = []
        
        sel = self.scene().selectedItems()
        for item in sel:
            if isinstance(item, NodeUi):
                nodes.append(item)
        
        return nodes
    
    """
    def _selectedAttributes(self):
        from . import AttributeUi    
        attributes = []
        
        sel = self.scene().selectedItems()
        for item in sel:
            if isinstance(item, AttributeUi):
                attributes.append(item)
        
        return attributes
    """
    
    def setZoom(self, zoom):
        self._zoom = zoom
        
        if zoom >= 1.0:
            self._zoom = 1.0
        elif zoom <= 0.1:
            self._zoom = 0.1
        
        transform = self.transform()
        newTransform = QtGui.QTransform.fromTranslate(transform.dx(), transform.dy())
        newTransform.scale(self._zoom, self._zoom)
        self.setTransform(newTransform)
        
        self.scene().setZoom(self._zoom)

    def zoomIn(self):
        self.setZoom(self._zoom+0.05)

    def zoomOut(self):
        self.setZoom(self._zoom-0.05)
    
    
