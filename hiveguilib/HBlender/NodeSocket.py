from ..HUtil.Node import colors
import bpy
from math import *

socketclasses = {}


class HiveNodeSocket:
    def draw_shape(self, context, node):
        return self._shape

    def draw_color(self, context, node):
        ret = self._color
        if len(self._color) == 1:
            ret = ret[0]  # #huh? oh well...

        return ret

    def draw(self, context, layout, node, text):
        # ##TODO
        pass

    def check_update(self):
        tangentLength = 60  # TODO: get this from NodeSocket-location or NodeLink vector (when added to API)
        spread = 60.0 / 180.0 * pi
        nr_con = len(self.links)

        for ind, link in enumerate(self.links):
            dev = (ind - nr_con / 2.0 + 0.5) * min(spread, pi / (nr_con + 2))
            tx = tangentLength * cos(dev)
            ty = tangentLength * sin(dev)
            try:
                if self.in_out == "OUT":
                    link.set_initial_tangent(tx, -ty)

                elif self.in_out == "IN":
                    link.set_final_tangent(tx, -ty)

            except AttributeError:
                pass


def register():
    """
    NodeSocket colors and shapes are *NOT* saved in the .blend
    Therefore, we must register a separate Hive NodeSocket type for every possible color and shape
    """
    for shape in "circle", "square":
        for color in colors:
            _color = tuple([v / 255.0 for v in color]) + (0.8,),
            _shape = "circle"
            if shape == "circle":
                _shape = "CIRCLE"
            if shape == "square":
                _shape = "DIAMOND"
            for complement in True, False:
                name = 'HiveNodeSocket%d' % (len(socketclasses) + 1)
                d = dict(bl_idname=name, bl_label=name, _shape=_shape, _color=_color)
                if complement:
                    d["bl_hide_label"] = True
                    d["bl_shared_row"] = True

                socketclass = type(name, (bpy.types.NodeSocket, HiveNodeSocket,), d)
                socketclasses[shape, color, complement] = socketclass
                if not complement:
                    socketclasses[shape, color] = socketclass
                bpy.utils.register_class(socketclass)


def unregister():
    for socketclass in socketclasses.values():
        try:
            bpy.utils.unregister_class(socketclass)
        except RuntimeError:
            pass

    socketclasses.clear()
