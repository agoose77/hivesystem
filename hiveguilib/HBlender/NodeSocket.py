from ..HUtil.Node import colors
import bpy
from math import *

socketclasses = {}


class HiveNodeSocket:
    """Custom HIVE node socket"""

    def draw_shape(self, context, node):
        """Return shape type to draw socket with

        :param context: blender context struct
        :param node: current node
        """
        return self._shape

    def draw_color(self, context, node):
        """Return color to draw socket with

        :param context: blender context struct
        :param node: current node
        """
        ret = self._color
        if len(self._color) == 1:
            ret = ret[0]  # #huh? oh well...

        return ret

    # TODO implement this?
    def draw(self, context, layout, node, text):
        pass

    def check_update(self):
        """Update custom link type between sockets"""
        tangent_length = 60  # TODO: get this from NodeSocket-location or NodeLink vector (when added to API)
        spread = radians(tangent_length)
        connection_count = len(self.links)
        step_angle = min(spread, pi / (connection_count + 2))

        for index, link in enumerate(self.links):
            slope = (index - (connection_count / 2.0) + 0.5) * step_angle
            tangent_x = tangent_length * cos(slope)
            tangent_y = tangent_length * sin(slope)

            try:
                if self.in_out == "OUT":
                    link.set_initial_tangent(tangent_x, -tangent_y)

                elif self.in_out == "IN":
                    link.set_final_tangent(tangent_x, -tangent_y)

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
