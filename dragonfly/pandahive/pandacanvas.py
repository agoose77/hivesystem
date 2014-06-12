import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from ..canvas import canvasdrone
import functools

from .pandabgrid import pandabgrid
from .panda_str import panda_str
from .panda_mstr import panda_mstr
from . import pandaimage
from .build_canvasdrone import build_canvasdrone

pandacanvas_bgrid = build_canvasdrone(
    pandabgrid,
    "pandacanvas_bgrid",
    "draw",
    ("object", "bgrid"),
    object,
)
pandacanvas_image = build_canvasdrone(
    pandaimage.pandaimage,
    "pandacanvas_image",
    "draw",
    ("object", "image"),
    pandaimage.canvasdrone_baseclass,
)

pandacanvas_str = build_canvasdrone(
    panda_str,
    "pandacanvas_str",
    "draw",
    "str",
    object,
)

pandacanvas_mstr = build_canvasdrone(
    panda_mstr,
    "pandacanvas_mstr",
    "draw",
    "mstr",
    object,
)


class pandacanvas(canvasdrone):
    def __init__(self):
        canvasdrone._wrapped_hive.__init__(self)
        self.d_bgrid = pandacanvas_bgrid()
        self.d_str = pandacanvas_str()
        self.d_mstr = pandacanvas_mstr()
        self.d_image = pandacanvas_image()

    def place(self):
        self.d_bgrid.place()
        self.d_str.place()
        self.d_mstr.place()
        self.d_image.place()
        canvasdrone._wrapped_hive.place(self)

