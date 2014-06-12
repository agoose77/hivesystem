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

import weakref
from ..anyQt import QtGui, QtCore

from . import ConnectionHook
from math import *

def cartToPolar(x, y):
    r = sqrt(x*x+y*y)
    theta = atan2(y,x)
    return r, theta
    
def polarToCart(r, theta):
    return r*cos(theta),r*sin(theta)        

def averagePolars(p1, p2):
    r1, theta1 = p1
    r2, theta2 = p2
    thmin, thmax = theta1, theta2
    if thmin > thmax: 
        thmin, thmax = thmax, thmin
    thdif1 = thmax - thmin
    thdif2 = thmin - thmax + 2 * pi
    if thdif1 < thdif2: 
        theta = thmin + 0.5 * thdif1
    else:
        theta = thmax + 0.5 * thdif2
        if theta > pi: theta -= 2 * pi
    r = (r1+r2)/2.0
    return r, theta
    
def interpolateTangents(t1, t2):
    p1 = cartToPolar(t1.x(), t1.y())
    p2 = cartToPolar(t2.x(), t2.y())
    r, theta = averagePolars(p1, p2)
    r = 0.5 * r
    r = min(r, 100)
    x,y = polarToCart(r, theta)
    return QtCore.QPointF(x,y)

class Connection(QtGui.QGraphicsItem):
    _startHook = None
    _endHook = None
    def __init__(self, startHook, endHook = None, id_ = None):
        QtGui.QGraphicsItem.__init__(self, None, startHook.scene())
        
        if id_ is None: id_ = id(self)
        self.id = id_
        
        self._rect = QtCore.QRectF(0, 0, 0, 0)
   
        self._color = startHook.colorRef()
        self._pen = QtGui.QPen(self._color)
        self._isTempConnection = False
        self._path = QtGui.QPainterPath()
        self._interpoints = []

        self.setStartHook(startHook)
        self.setEndHook(endHook)
        
        if endHook is None:
            # creating a dummy endHook for temporary connection dragging, 
            #  the "input" and shape/style parameters have no effect
            dummy = ConnectionHook(startHook.parentAttributeUi(), \
             "input", "square", self._activeStyle, parentItem = self)
            self.setEndHook(dummy)
            self.endHook().boundingRect().setSize(QtCore.QSizeF(2.0, 2.0))
            self._isTempConnection = True
            
        self.updateStartPos()
        
        self.setZValue(-1.0)
        self.setActive(False)
    
    def h_setInterpoints(self, interpoints):
        s = self.scenePos()
        sx, sy = s.x(), s.y()         
        self._interpoints = [QtCore.QPointF(x-sx,-y-sy) for x,y in interpoints]
        
    def insertInterpoint(self, index, coordinate):
        if index is None: 
            self._interpoints.append(coordinate)
        else:
            self._interpoints.insert(index, coordinate)

    def removeInterpoint(self, index):
        self._interpoints.pop(self._interpoints)
            
    def _difDistance(self, pos, coor):
        return pos - coor
        
    def findNearestInterpoints(self, coordinate):
        points = []
        
        startHook = self._startHook()
        startPos = startHook.scenePos() + startHook.boundingRect().center()
        points.append(startPos)
        
        points += self._interpoints       
        distances = [(pnr,self._difDistance(p,coordinate)) 
                     for pnr, p in enumerate(points)]        
        
        if self.endHook():
            endHook = self.endHook()
            endPos = endHook.scenePos() + endHook.boundingRect().center()
            distances.append((-1, self._difDistance(endPos, coordinate)))
        
        if len(distances) == 1: return distances[0][0], None
        
        distances.sort(key=lambda item:item[1])
        return distances[0][0], distances[1][0]
            
    def setActive(self, active):
        assert active in (True, False), active
        
        if active:
          self._pen.setWidth(3)
        else:
          self._pen.setWidth(2)
        value = self._activeStyle
        
        if value == "dashed":
            self._pen.setStyle(QtCore.Qt.DashLine)
        elif value == "solid":
            self._pen.setStyle(QtCore.Qt.SolidLine)
        elif value == "dot":
            self._pen.setStyle(QtCore.Qt.DotLine)
        else:
            raise ValueError("Unknown pen style '%s'" % value)    

    def setSelected(self, selected):
        assert selected in (True, False), selected
        
        self.setActive(selected)
        if selected:
            self._pen.setWidth(5)    
        
        
    def deleteIt(self):
        if self.scene():
            self.scene().removeItem(self)
        self.setEndHook(None)
        self.setStartHook(None)
            
            
    def updateStartPos(self):
        startHook = self._startHook()
        self.setPos(startHook.scenePos() + startHook.boundingRect().center())
        
        self.updatePath()
    
    def updateEndPos(self):
        self.updatePath()
    
    def setColor(self, color):
        if isinstance(color, tuple):
            color = QtGui.QColor(*color)
        else:
            color = QtGui.QColor(color)    
        self._color = color

    def setStartHook(self, connectionHook):
        if self.startHook():
            self.startHook().removeConnection(self)
            self.startHook().parentAttributeUi().parentNodeUi().update()
        
        self._startHook = None
        self._activeStyle = "dot"
        if connectionHook is not None:
            self._startHook = weakref.ref(connectionHook)
            connectionHook.addConnection(self)
            self._activeStyle = connectionHook._style
        
    def startHook(self):
        if self._startHook is None: return None
        return self._startHook()
    
    def setEndHook(self, connectionHook):
        if self.endHook():
            self.endHook().removeConnection(self)
            self.endHook().parentAttributeUi().parentNodeUi().update()
        
        self._endHook = None
        if connectionHook is not None:
            connectionHook.addConnection(self)
            self._endHook = weakref.ref(connectionHook)
    
    def endHook(self):
        if self._endHook is None: return None
        return self._endHook()
            
    def findClosestHook(self):
        closestHook = None
        
        collidingItems = self.endHook().collidingItems(QtCore.Qt.IntersectsItemBoundingRect)
        for collidingItem in collidingItems:
            if type(collidingItem) is ConnectionHook:
                if collidingItem.isInput() and collidingItem.isVisible():
                    closestHook = collidingItem
                break
        
        return closestHook
    
    def updatePath(self):        
        endHook = self.endHook()
        if endHook is None: return

        self.prepareGeometryChange()
        endPos = self.mapFromItem(endHook, 0.0, 0.0) + endHook.boundingRect().center()
        if not len(self._interpoints):
            tangentLength = (abs(endPos.x()) / 2.0) + (abs(endPos.y()) / 4.0)
            tangentLength2 = tangentLength
        else:
            firstPos = self._interpoints[0]
            tangentLength = (abs(firstPos.x()) / 2.0) + (abs(firstPos.y()) / 4.0)    
            lastPos = self._interpoints[-1]
            lastSeg = endPos - lastPos
            tangentLength2 = (abs(lastSeg.x()) / 2.0) + (abs(lastSeg.y()) / 4.0)    

        spread = 60.0/180.0 * pi
        ind, nr_con = self.startHook().connectionIndex(self)
        dev = (ind - nr_con/2.0 + 0.5) * min(spread, pi/(nr_con+2))
        tx = tangentLength * cos(dev)
        ty = tangentLength * sin(dev)
        startTangent = QtCore.QPointF(tx, ty)        
        
        endTangent = QtCore.QPointF(endPos.x() - tangentLength2, endPos.y())  

        path = QtGui.QPainterPath()        
        currTangent = startTangent
        currPos = QtCore.QPointF(0.0,0.0)
        for pnr, p in enumerate(self._interpoints):
            if pnr == len(self._interpoints)-1:
                nextp = endPos
            else:
                nextp = self._interpoints[pnr+1]    
            nextTangent = interpolateTangents((p-currPos), (nextp - p))
            path.cubicTo(currTangent, p-nextTangent, p)
            currTangent = p+nextTangent
            currPos = p
        path.cubicTo(currTangent, endTangent, endPos)
        
        strokeWidth = self._pen.widthF()
        rect = path.boundingRect().adjusted(-strokeWidth, -strokeWidth, strokeWidth, strokeWidth)
        
        self._path = path
        self._rect = rect

    def boundingRect(self):
        return self._rect
    
    def paint(self, painter, option, widget):
        self._pen.setColor(self._color)
        painter.setPen(self._pen)
        painter.drawPath(self._path)
