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

import weakref
from ..anyQt import QtGui, QtCore

from . import nodeCanvas
from .connection import Connection
from .connectionHook import ConnectionHook
from .. import Attribute


class AttributeUi(QtGui.QGraphicsWidget):
    def __init__(self, parentNodeUi, params):
        QtGui.QGraphicsWidget.__init__(self, parentNodeUi)
        assert isinstance(params, Attribute)

        self._parentNodeUi = weakref.ref(parentNodeUi)
        self._params = params
        self._spacerConstant = 5.0
        self._label = QtGui.QGraphicsSimpleTextItem(self)

        self._inputHook = None
        if params.inhook is not None:
            self._inputHook = ConnectionHook(self, "input", \
                                             params.inhook.shape, params.inhook.style,
                                             hoverText=params.inhook.hover_text,
                                             orderDependent=params.inhook.order_dependent
            )
            self.setHooksColor("input", QtGui.QColor(*params.inhook.color))
            self._inputHook.setVisible(params.inhook.visible)
        self._outputHook = None
        if params.outhook is not None:
            self._outputHook = ConnectionHook(self, "Output", \
                                              params.outhook.shape, params.outhook.style,
                                              hoverText=params.outhook.hover_text,
                                              orderDependent=params.outhook.order_dependent
            )
            self.setHooksColor("Output", QtGui.QColor(*params.outhook.color))
            self._outputHook.setVisible(params.outhook.visible)

        self._label.setBrush(parentNodeUi.labelsColor())
        label = self._params.name
        if self._params.label is not None:
            label = self._params.label
        self._labelText = label
        self.setValue(self._params.value)
        self.setVisible(self._params.visible)

    def labelColor(self):
        return self._label.brush().color()

    def setValue(self, value):
        text = self._labelText
        if value is not None:
            if self._params.value_on_newline:
                text += ":\n  "
            else:
                text += ": "
            value2 = value
            pos = value.find("\n")
            if pos > -1:
                value2 = value[:pos] + " ..."
            if len(value2) > 34:
                value2 = value2[:30] + " ..."
            text += value2
        self._label.setText(text)

    def label(self):
        return self._label

    def toolTip(self):
        return self._params.tooltip

    def _disconnected(self):
        if self._inputHook:
            if self._inputHook._connections:
                self._inputHook._connections[0].deleteIt()

    def setHooksColor(self, io, color, mixedColor=False):
        hook = None
        if io == "input":
            hook = self._inputHook
        else:
            hook = self._outputHook

        hook.setColor(color)
        hook.setMixedColor(mixedColor)

    def parentNodeUi(self):
        parent = None
        if self._parentNodeUi:
            parent = self._parentNodeUi()

        return parent

    def updateLayout(self):
        height = self._label.boundingRect().height()

        hookY = 0
        if self._outputHook:
            hookY = (height - self._outputHook.boundingRect().height()) / 2.0
        elif self._inputHook:
            hookY = (height - self._inputHook.boundingRect().height()) / 2.0

        inputHookWidth = self._spacerConstant * 2.0
        if self._inputHook:
            self._inputHook.setPos(0.0, hookY)

        self._label.setPos(inputHookWidth + self._spacerConstant, 0)

        if self._outputHook:
            self._outputHook.setPos(self._label.pos().x() + self._label.boundingRect().width() + self._spacerConstant,
                                    hookY)

            self.resize(self._outputHook.pos().x() + self._outputHook.boundingRect().width(), height)
        else:
            self.resize(self._label.pos().x() + self._label.boundingRect().width(), height)

    def setParentNodeUi(self, nodeUi):
        self.setParentItem(None)
        if self.scene():
            if self in self.scene().items():
                self.scene().removeItem(self)

        if self._parentNodeUi:
            parentNodeUi = self._parentNodeUi()
            if self in parentNodeUi._attributeUis:
                del parentNodeUi._attributeUis[parentNodeUi._attributeUis.index(self)]

        if nodeUi:
            self._parentNodeUi = weakref.ref(nodeUi)

            self.setParentItem(nodeUi)

            if self not in nodeUi._attributeUis:
                nodeUi._attributeUis.append(self)

        else:
            self._parentNodeUi = None

    def deleteIt(self):
        if self._outputHook:
            self._outputHook.deleteIt()

        if self._inputHook:
            self._inputHook.deleteIt()

        self.setParentNodeUi(None)
        
