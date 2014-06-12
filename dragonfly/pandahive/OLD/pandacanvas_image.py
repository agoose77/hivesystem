import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

try:
    from panda3d.core import NodePath
    from panda3d.core import CardMaker
    from pandac.PandaModules import TransparencyAttrib
    import panda3d
except ImportError:
    panda3d = None


class pandacanvas_image(object):
    def draw_image(self, image, box, identifier="", parameters=None):
        cm = CardMaker(identifier)
        tex = self.get_loader().loadTexture(image.value)

        if box.mode == "pixels":
            parent2d = self.get_parent_pixel2d()
        elif box.mode == "standard":
            parent2d = self.get_parent_render2d()
        elif box.mode == "aspect":
            parent2d = self.get_parent_aspect2d()

        node = NodePath(cm.generate())
        node.setTexture(tex)

        if parameters is not None:
            if hasattr(parameters, "transparency") and parameters.transparency == True:
                node.setTransparency(TransparencyAttrib.MAlpha)

        node.setPos(box.x, 0, box.y + box.sizey)
        node.setScale(box.sizex, 1, -box.sizey)
        node.setBin("fixed", self.get_next_sortid())
        node.setDepthTest(False)
        node.setDepthWrite(False)
        node.reparentTo(parent2d)
        return (node, image, box, parameters)

    def update_image(self, imageobject):
        node, image, box, parameters = imageobject
        # TODO: box update
        #TODO: parameter update
        tex = loader.loadTexture(image.value)
        node.setTexture(tex)

    def remove_image(self, imageobject):
        node, image, box, parameters = imageobject
        node.removeNode()

    def _set_loader(self, get_loader):
        self.get_loader = get_loader

    def place(self):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        libcontext.socket(("panda", "noderoot", "loader"), socket_single_required(self._set_loader))

        libcontext.plugin(("canvas", "draw", ("object", "image")), plugin_supplier(self.draw_image))
        libcontext.plugin(("canvas", "update", ("object", "image")), plugin_supplier(self.update_image))
        libcontext.plugin(("canvas", "remove", ("object", "image")), plugin_supplier(self.remove_image))
  
  
