import libcontext, bee
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from .box2d import std_to_pixels, pixels_to_std


class mousearea(bee.drone):
    def __init__(self):
        self.areas = {}
        self.areanames = []

    def get_mousebutton_event(self, event):
        canvasx, canvasy = self.canvas_size()
        x, y = event[1]
        for areaname in reversed(self.areanames):
            area = self.areas[areaname]
            a = area.to_std(canvasx, canvasy)
            px = 2 * (x - a.x) / a.sizex - 1
            py = 2 * (y - a.y) / a.sizey - 1
            if px < -1 or px > 1:
                continue
            if py < -1 or py > 1:
                continue
            e = bee.event("mousearea", areaname, event[0], (px, py))
            self.send_event(e)
            break

    def register(self, areaname, area):
        if areaname in self.areas.keys(): raise KeyError(areaname)
        self.areanames.append(areaname)
        self.areas[areaname] = area

    def update(self, areaname, area):
        if areaname not in self.area.keys(): return
        self.areas[areaname] = area

    def remove1(self, areaname):
        self.areas.pop(areaname)

    def remove2(self, areaname):
        self.areas.pop(areaname, None)

    def set_canvas_size_func(self, canvas_size_func):
        self.canvas_size = canvas_size_func

    def set_send_event(self, send_event):
        self.send_event = send_event

    def place(self):
        libcontext.socket(("evin", ("input", "mouse")), socket_flag())
        libcontext.plugin(("evin", ("input", "mousearea")), plugin_flag())
        listener = plugin_single_required(("leader", self.get_mousebutton_event, ("mouse", "buttonpressed")))
        libcontext.plugin(("evin", "listener"), listener)
        libcontext.socket(("evin", "event"), socket_single_required(self.set_send_event))
        libcontext.socket(("canvas", "size"), socket_single_required(self.set_canvas_size_func))

        p = plugin_supplier(self.register)
        libcontext.plugin(("canvas", "mousearea", "register"), p)
        p = plugin_supplier(self.update)
        libcontext.plugin(("canvas", "mousearea", "update"), p)
        p = plugin_supplier(self.remove1)
        libcontext.plugin(("canvas", "mousearea", "remove1"), p)
        p = plugin_supplier(self.remove2)
        libcontext.plugin(("canvas", "mousearea", "remove2"), p)
        p = plugin_supplier(self.areas)
        libcontext.plugin(("canvas", "mousearea", "mouseareas"), p)
  
