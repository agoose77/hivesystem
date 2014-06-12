try:
    import direct.showbase.ShowBase
    from direct.showbase.ShowBase import ShowBase
    import panda3d
except ImportError:
    panda3d = None
    ShowBase = object

import bee, libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *


class pandawindow(bee.drone, ShowBase):
    def __init__(self):
        self.initialized = False
        self.initialized2 = False

    def init(self):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        if self.initialized: return
        try:
            ShowBase.__init__.im_func(self)
        except StandardError:
            self.__dict__.update(
                direct.showbase.ShowBase.__builtin__.base.__dict__
            )
        self.initialized = True
        self.disableMouse()

    def get_render(self):
        try:
            ret = self.render
        except AttributeError:
            self.init()
            ret = self.render
        return ret

    def get_render2d(self):
        try:
            ret = self.render2d
        except AttributeError:
            self.init()
            ret = self.render2d
        return ret

    def get_aspect2d(self):
        try:
            ret = self.aspect2d
        except AttributeError:
            self.init()
            ret = self.aspect2d
        return ret

    def get_pixel2d(self):
        try:
            ret = self.pixel2d
        except AttributeError:
            self.init()
            ret = self.pixel2d
        return ret

    def get_loader(self):
        try:
            ret = self.loader
        except AttributeError:
            self.init()
            ret = self.loader
        return ret

    def get_camera(self):
        try:
            ret = self.camera
        except AttributeError:
            self.init()
            ret = self.camera
        return ret

    def get_camera_matrix(self):
        from ..scene.matrix import matrix

        return matrix(self.get_camera(), "NodePath")

    def place(self):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")

        libcontext.plugin("startupfunction", plugin_single_required(self.init))
        libcontext.plugin(("panda", "window"), plugin_supplier(self))
        libcontext.plugin(("panda", "noderoot", "render"), plugin_supplier(self.get_render))
        libcontext.plugin(("panda", "noderoot", "render2d"), plugin_supplier(self.get_render2d))
        libcontext.plugin(("panda", "noderoot", "aspect2d"), plugin_supplier(self.get_aspect2d))
        libcontext.plugin(("panda", "noderoot", "pixel2d"), plugin_supplier(self.get_pixel2d))
        libcontext.plugin(("panda", "noderoot", "loader"), plugin_supplier(self.get_loader))

        libcontext.plugin("get_camera", plugin_supplier(self.get_camera))

        libcontext.plugin(("panda", "camera"), plugin_supplier(self.get_camera))
        libcontext.plugin("camera", plugin_supplier(self.get_camera_matrix))
        libcontext.plugin(("camera", "NodePath"), plugin_supplier(self.get_camera))
        libcontext.plugin(("canvas", "size"), plugin_supplier(self.getSize))

    def __getattr__(self, attr):
        if self.initialized2: raise AttributeError(attr)
        self.initialized2 = True
        self.init()
        return getattr(self, attr)
