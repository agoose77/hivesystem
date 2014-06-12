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

import copy
import weakref
from ..anyQt import QtGui, QtCore

from . import NodeCanvas
from . import NodeUiScene
###from connection import Connection
###from connectionHook import ConnectionHook
from . import AttributeUi
from . import NodeView

class NodeUi(QtGui.QGraphicsWidget):    
    def __init__(self, name, attributes, tooltip = None):
        QtGui.QGraphicsWidget.__init__(self)
        
        self._spacerConstant = 5.0
        self._label = QtGui.QGraphicsSimpleTextItem(self)        
        self._shapePen = QtGui.QPen(QtCore.Qt.NoPen)
        self._attributeUis = []
        self._brush = QtGui.QBrush(self.color())
        self._selectedColor = QtGui.QColor(255, 255, 255)
        self._dropShadowEffect = QtGui.QGraphicsDropShadowEffect()
        self._showingRightClickMenu = False
        self._rightClickMenuItems = []
        self._doubleClicked = False
        self._zValue = self.zValue()
        self._currentMagnifyFactor = 1.0
        self._moving = False
        self._deleted = False
        
        self.setGraphicsEffect(self._dropShadowEffect)
        
        self._dropShadowEffect.setOffset(0.0, 10.0)
        self._dropShadowEffect.setBlurRadius(8.0)
        self._dropShadowEffect.setColor(QtGui.QColor(0, 0, 0, 50))
        
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        self._label.setBrush(self.labelsColor())
        
        self._shapePen.setColor(self._selectedColor)
        self._shapePen.setWidthF(1.5)
        
        self._label.setText(name)
        if tooltip is not None: self.setToolTip(tooltip)
        self._build(attributes)

        self._lastPos = self.scenePos()

    
    def _magnifyAnimStep(self, frame):
        step = frame / NodeView._animSteps
        invStep = 1.0 - step
        
        self.setScale((self.scale() * invStep) + ((1.0 * self._currentMagnifyFactor) * step))
        
        for attr in self._attributeUis:
            if attr._inputHook:
                attr._inputHook.updateWorldPos()
            if attr._outputHook:
                attr._outputHook.updateWorldPos()
                
        self.scene().update()
        
    def _magnify(self, factor):
        self._currentMagnifyFactor = factor
        timer = QtCore.QTimeLine(NodeView._animSpeed, self)
        timer.setFrameRange(0, NodeView._animSteps)
        
        self.connect(timer, QtCore.SIGNAL("frameChanged(int)"), self._magnifyAnimStep);
        
        timer.start()
    
    def hoverEnterEvent(self, event):
        if not NodeView._panning:
            if NodeView._lastHoveredItem is not self:
                if NodeView._lastHoveredItem:
                    NodeView._lastHoveredItem.hoverLeaveEvent(None)
                    
                zoom = self.scene().zoom()
                if zoom < 0.6:
                    factor =  0.7 / zoom
                    
                    self.setTransformOriginPoint(self.rect().center())
                    self._magnify(factor)
                
                    NodeView._lastHoveredItem = self
                
                    self.setZValue(9999999)
        
    def hoverLeaveEvent(self, event):
        if NodeView._lastHoveredItem is self:
            self._magnify(1.0)
            
            self.setZValue(self._zValue)
            NodeView._lastHoveredItem = None
    
    
    def _clearAttributeUis(self):
        for attrUi in self._attributeUis:
            attrUi.setParent(None)
        
        self._attributeUis = []
        
    def setName(self, name):
        self._label.setText(name)
        self.updateLayout()

    
    def addRightClickMenuItem(self, label, callback):
        self._rightClickMenuItems.append({label: callback})
    
    def showRightClickMenu(self):
        #        self._showingRightClickMenu = True???
        menu = QtGui.QMenu(NodeCanvas.focusedInstance())
        raise Exception("TODO")
        titleAction = menu.addAction(self.coralNode().name() + ":")
        titleAction.setDisabled(True)
        
        for item in self._rightClickMenuItems:
            label = item.keys()[0]
            callback = item.values()[0]

            menu.addAction(label, callback)
        
        cursorPos = QtGui.QCursor.pos()
        menu.move(cursorPos.x(), cursorPos.y())
        menu.show()
                               
    def shapePen(self):
        return QtGui.QPen(self._shapePen)
           
    def color(self):
        return QtGui.QColor(0, 0, 0)
    
    def labelsColor(self):
        return QtGui.QColor(255, 255, 255)
    
    def onSelected(self):
        if self._deleted: return
        if self.isSelected():
            self._shapePen.setStyle(QtCore.Qt.SolidLine)
        else:
            self._shapePen.setStyle(QtCore.Qt.NoPen)

        nodes = []            
        sel = self.scene().selectedItems()
        for item in sel:
            if isinstance(item, NodeUi):
                nodes.append(item)

        canvas = self.scene()._hqt
        if canvas: 
            if len(nodes) == 0: canvas().gui_deselects()
            else: canvas().gui_selects(nodes)
        
    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedHasChanged:
            self.onSelected()
            
        return value
                    
    def updateLayout(self):
        labelWidth = self._label.boundingRect().width()
        width = labelWidth
        yPos = self._label.boundingRect().bottom() + self._spacerConstant
                
        for attributeUi in self._attributeUis:
            if attributeUi.isVisible():
                attributeUi.updateLayout()
            
                attributeUi.setPos(self._spacerConstant, yPos)
                yPos += attributeUi.boundingRect().height()
            
                attributeWidth = attributeUi.boundingRect().width()
                if attributeWidth > width:
                    width = attributeWidth
        
        for attributeUi in self._attributeUis:
            if attributeUi.isVisible():
                outHook = attributeUi._outputHook
                if outHook is not None:
                    outHook.setPos(width - outHook.boundingRect().width(), outHook.pos().y())
        
        width = self._spacerConstant + width + self._spacerConstant
        self._label.setPos((width - labelWidth) / 2.0, self._spacerConstant)
        
        self.resize(width, yPos + self._spacerConstant)
        self.update()
        
    def paint(self, painter, option, widget):
        shape = QtGui.QPainterPath()
        shape.addRoundedRect(self.rect(), 2, 2)
        
        painter.setPen(self._shapePen)
        painter.setBrush(self._brush)
        painter.drawPath(shape)
    
    def deleteIt(self):
        self._deleted = True
        if self.isSelected():
            self.setSelected(False)

        attrs = copy.copy(self._attributeUis)
        for attr in attrs:
            attr.deleteIt()
        
        if self.scene():
            if self in self.scene().items():
                self.scene().removeItem(self)
                    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            pass
        else:
            QtGui.QGraphicsWidget.mousePressEvent(self, event)
    
    def setPos(self, *pos):
        if len(pos) == 1:
            p = QtCore.QPointF(pos[0])
        else:
            p = QtCore.QPointF(*pos)
        self._lastPos = p
        QtGui.QGraphicsWidget.setPos(self, p)
        
    def mouseReleaseEvent(self, event):
        if self._moving:
            canvas = self.scene()._hqt
            ok = True
            if canvas is not None:
                offset = self.scenePos() - self._lastPos
                ok = canvas().gui_moves_node(self, offset)
            if ok: 
                self._lastPos = self.scenePos()
            else:
                QtGui.QGraphicsWidget.setPos(self, self._lastPos)    
            self._moving = False    
        if self._doubleClicked:
            self._doubleClicked = False
            #self._openThis()
        elif event.button() == QtCore.Qt.RightButton:
            self.showRightClickMenu()
        else:
            QtGui.QGraphicsWidget.mouseReleaseEvent(self, event)
    
    def mouseMoveEvent(self, event):
        self._moving = True
        if self._doubleClicked:
            return
        else:
            QtGui.QGraphicsWidget.mouseMoveEvent(self, event)
    
    def mouseDoubleClickEvent(self, event):
        self._doubleClicked = True
    
    def _build(self, attributes):
        for attributeParams in attributes:
            attributeUi = AttributeUi(self, attributeParams)
            self._attributeUis.append(attributeUi)

    def getAttributeUi(self, name):
        for a in self._attributeUis:
            if a._params.name == name: return a
        #raise KeyError(name) ###TODO
      
    
