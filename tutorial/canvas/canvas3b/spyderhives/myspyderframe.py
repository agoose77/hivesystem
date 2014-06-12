from bee.spyderhive import spyderframe, SpyderMethod

from bee.drone import dummydrone
from dragonfly.canvas import canvasargs
from libcontext.pluginclasses import plugin_single_required


def show_coloredtextbox(ctb):
    ctb2 = ctb.to_coloredtextbox()
    args = canvasargs(ctb2)
    p = plugin_single_required(args)
    pattern = ("canvas", "show", "init", ("object", "coloredtextbox"))
    d = dummydrone(plugindict={pattern: p})
    return d.getinstance()


class myspyderframe(spyderframe):
    SpyderMethod("make_bee", "ColoredTextBox", show_coloredtextbox)