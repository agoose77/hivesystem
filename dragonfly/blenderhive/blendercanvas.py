import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from ..canvas import canvasdrone
import functools

from .blenderbgrid import blenderbgrid
from .blender_str import blender_str
from .blender_mstr import blender_mstr
from . import blenderimage
from .build_canvasdrone import build_canvasdrone

blendercanvas_bgrid = build_canvasdrone(
    blenderbgrid,
    "blendercanvas_bgrid",
    "draw",
    ("object", "bgrid"),
    object,
)

blendercanvas_image = build_canvasdrone(
    blenderimage.blenderimage,
    "blendercanvas_image",
    "draw",
    ("object", "image"),
    blenderimage.canvasdrone_baseclass,
)

blendercanvas_str = build_canvasdrone(
    blender_str,
    "blendercanvas_str",
    "draw",
    "str",
    object,
)

blendercanvas_mstr = build_canvasdrone(
    blender_mstr,
    "blendercanvas_mstr",
    "draw",
    "mstr",
    object,
)


class blendercanvas(canvasdrone):
    def __init__(self):
        canvasdrone._wrapped_hive.__init__(self)
        self.d_bgrid = blendercanvas_bgrid()
        self.d_str = blendercanvas_str()
        self.d_mstr = blendercanvas_mstr()
        self.d_image = blendercanvas_image()

    @staticmethod
    def canvas_size():
        import bge

        x = bge.render.getWindowWidth()
        y = bge.render.getWindowHeight()
        return x, y

    def place(self):
        libcontext.plugin(("canvas", "size"), plugin_supplier(self.canvas_size))
        self.d_bgrid.place()
        self.d_str.place()
        self.d_mstr.place()
        self.d_image.place()
        canvasdrone._wrapped_hive.place(self)


"""
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from ..canvas import canvasdrone
from .blendercanvas_bgrid import blendercanvas_bgrid
from .blendercanvas_mstr import blendercanvas_mstr
from .blendercanvas_image import blendercanvas_image
import functools

class blendercanvas(canvasdrone,
                  blendercanvas_bgrid,
                  blendercanvas_mstr,
                  blendercanvas_image,
                 ): #call place() explicitly for all mixins!
  def __init__(self):
    canvasdrone._wrapped_hive.__init__(self)
    self._render2d = None
    self._aspect2d = None
    self._pixel2d = None

  def get_canvas_size(self, canvas_sizefunc):
    self.canvas_size = canvas_sizefunc

  def _set_render2d(self,get_render2d):
    self.get_render2d = get_render2d
  def _set_aspect2d(self,get_aspect2d):
    self.get_aspect2d = get_aspect2d
  def _set_pixel2d(self,get_pixel2d):
    self.get_pixel2d = get_pixel2d
  @staticmethod
  def canvas_size():
    import bge 
    x = bge.render.getWindowWidth()
    y = bge.render.getWindowHeight()
    return x,y
    
  def place(self):
    libcontext.socket(("blender", "noderoot", "pixel2d"), socket_single_required(self._set_pixel2d))
    libcontext.socket(("blender", "noderoot", "render2d"), socket_single_required(self._set_render2d))
    libcontext.socket(("blender", "noderoot", "aspect2d"), socket_single_required(self._set_aspect2d))
    libcontext.plugin(("canvas","size"), plugin_supplier(self.canvas_size))

    #super() and stuff doesn't work, call place() explicitly for each mixin
    blendercanvas_bgrid.place(self)
    blendercanvas_mstr.place(self)
    blendercanvas_image.place(self) 

    #finally, call canvasdrone.place
    canvasdrone._wrapped_hive.place(self)
"""
