from .BlenderWidgets import BlenderDummyWidget, BlenderWrapWidget, BlenderEmptyWidget
import weakref
from .Layout import Layout
import logging
from . import Node, NodeTree
from . import level


class BlenderParameterArea:
    known = ('props-parameters', 'props-general', 'props-params', 'proptabs', 'props-metaparams', 'props-block')

    def __init__(self, parent):
        self.parent = parent
        self.subwindows = {}

    def newSubWindow(self, name):
        if name == "proptabs":
            p = BlenderParameterPanel(name, self)
            self.subwindows[name] = p
            return p
        raise NotImplementedError(name)

    def show(self):
        for win in self._subwindows: win.show()

    def draw(self, context, layout):
        for k in self.subwindows: assert k in self.known, k
        for sub in ('props-general', 'props-params', 'props-metaparams', 'props-block'):
            if sub not in self.subwindows: continue
            self.subwindows[sub].draw(context, layout)

    def __getattr__(self, attr):
        raise NotImplementedError


class BlenderToolArea:
    """
    Takes care of both panel and menu!
    """

    def __init__(self, parent):
        self.parent = parent
        self.subwindows = {}
        self.ptree = None

    def newSubWindow(self, name):
        raise NotImplementedError(name)

    def wrapwidget(self):
        return BlenderWrapWidget(self)

    def widget(self):
        return BlenderDummyWidget(self)

    def setWidget(self, widget):
        self.ptree = widget

    def show(self):
        pass

    def __getattr__(self, attr):
        raise NotImplementedError(attr)


class BlenderParameterPanel:
    def __init__(self, name, parent):
        self.name = name
        self.title = name.lstrip("props").lstrip("-").capitalize()
        self.parent = parent
        self.widget = None
        self._visible = False

    def newSubWindow(self, name):
        if name == "props-general":
            p = self.parent.parent._nodecanvas().bntm.controller_general.p()
        elif name == "props-block":
            p = self.parent.parent._nodecanvas().bntm.controller_block.p()
        else:
            p = BlenderParameterPanel(name, self.parent)
        self.parent.subwindows[name] = p
        return p

    def setWidget(self, widget):
        self.widget = widget

    def show(self):
        self._visible = True
        self.widget.show()

    def hide(self):
        self._visible = False
        self.widget.hide()

    def __getattr__(self, attr):
        raise NotImplementedError(attr, self.name)

    def draw(self, context, layout):
        if not self.widget or not self._visible or isinstance(self.widget, BlenderEmptyWidget): return
        if self.name == "props-metaparams":
            # for metaparams panel, don't draw the buttons if all parameters have been hidden
            hide = True
            for child in self.widget.children:
                if child._visible:
                    if not child.advanced or level.minlevel(context, 2):
                        hide = False
                        break
            if hide: return
        l = layout.column()
        l.label(self.title)
        self.widget.draw(context, l)
        layout.separator()


class BlenderToolPanel:
    def __init__(self, parent):
        self.name = name
        self.parent = parent

    def show(self):
        pass

    def __getattr__(self, attr):
        raise NotImplementedError(attr, self.name)


import bpy


class MainWindow(Layout):
    def __init__(self):
        self._subwindows = {}

    def setNodeCanvas(self, nodecanvas):
        self._nodecanvas = weakref.ref(nodecanvas)

    def _newSubWindow(self, name, parentwin=None):
        if name == "props":
            return BlenderParameterArea(self)
        elif name == "proptabs":
            return parentwin.newSubWindow(name)
        elif name.startswith("props"):
            return parentwin.newSubWindow(name)
        elif name == "workers":
            return BlenderToolArea(self)
        elif name == "drones":
            return BlenderToolArea(self)
        elif name == "spyderhive":
            return BlenderToolArea(self)
        raise NotImplementedError(name, parentwin)

    def newSubWindow(self, name, triggered=False):
        if triggered:
            if name in self._subwindows: return self._subwindows[name]
        else:
            assert name not in self._subwindows, name
        win = self._layout(name)
        self._subwindows[name] = win
        return win

    def getSubWindow(self, name):
        raise NotImplementedError

    def show(self):
        for win in self._subwindows: win.show()

    def popup(self, title, options):
        """
        Blender does not support blocking pop-ups
        Therefore, we must return None immediately (causing the operation to be rejected)
         and callbacks must have been associated with the options
        """
        self.result = None
        from .BlenderPopup import BlenderPopupMenu
        from .BlendManager import blendmanager

        # The callbacks must have been associated previously by the HBlender NodeCanvas
        assert blendmanager.popup_callbacks is not None \
               and len(blendmanager.popup_callbacks) == len(options)
        blendmanager.popup_options = options

        BlenderPopupMenu.bl_title = title  #doesn't work...
        menu = bpy.ops.wm.call_menu(name=BlenderPopupMenu.bl_idname)
        return None

    def supports_popup(self):
        return True

    def emptyWidget(self):
        return BlenderEmptyWidget(self)

    def add_menu(self, name):
        pass  # We don't need this in Blender

    def add_menu_action(self, menuname, name, callback,
                        icon=None, shortcut=None, statustip=None
    ):
        pass  # We don't need this in Blender

    def close(self):
        pass

    def draw_panel(self, context, layout):
        if "props" in self._subwindows:
            self._subwindows["props"].draw(context, layout)