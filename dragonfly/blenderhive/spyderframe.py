import Spyder, spyder, bee, libcontext
from bee import connect, Configure, ConfigureMultiple

from bee.spyderhive import spyderframe as spyderframe_orig, SpyderMethod, SpyderConverter

from ..canvas import box2d
import bee


class parameters: pass


from bee.drone import dummydrone
from ..canvas import canvasargs
from libcontext.pluginclasses import plugin_single_required


def show_image(i):
    b = i.box
    box = box2d(b.x, b.y, b.sizex, b.sizey, b.mode)
    params = parameters()
    if i.transparency: params.transparency = True
    args = canvasargs(i.image, i.identifier, box, params)
    plugin = plugin_single_required(args)
    pattern = ("canvas", "draw", "init", ("object", "image"))
    d1 = dummydrone(plugindict={pattern: plugin})
    return d1.getinstance()


def show_mousearea(i):
    i1 = bee.init("mousearea")
    b = i.box
    box = box2d(b.x, b.y, b.sizex, b.sizey, b.mode)
    i1.register(i.identifier, box)
    return i1


class spyderframe(spyderframe_orig):
    SpyderMethod("make_bee", "Image", show_image)
    SpyderMethod("make_bee", "MouseArea", show_mousearea)
  
