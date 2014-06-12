try:
    from panda3d.core import NodePath, TextNode
    import panda3d
except ImportError:
    panda3d = None


class panda_str(object):
    def __init__(self, canvasdrone, string, identifier, parentnode, parameters):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        self.node = None
        self._draw(string, identifier, parentnode, parameters)

    def update(self, string, identifier, parentnode, parameters):
        self._draw(string, identifier, parentnode, parameters)

    def remove(self):
        pass

    def _draw(self, string, identifier, parentnode, parameters):
        if self.node is not None: self.node.removeNode()
        tnode = TextNode(identifier)
        tnode.setText(string)
        # TODO: use more parameters
        if hasattr(parameters, "cardcolor"):
            tnode.setCardColor(*parameters.cardcolor)
            tnode.setCardAsMargin(0, 0, 0, 0)
            tnode.setCardDecal(True)
        aspect = True
        if hasattr(parameters, "aspect"):
            aspect = parameters.aspect
        node = NodePath(tnode)
        self._scale(tnode, node, aspect)
        node.reparentTo(parentnode)
        self.node = node

    def _scale(self, tnode, node, aspect):
        top, bottom = tnode.getTop(), tnode.getBottom()
        l, r = tnode.getLeft(), tnode.getRight()
        w, h = r - l, top - bottom
        scalex = 0
        if w > 0: scalex = 1.0 / w
        scaley = 0
        if h > 0: scaley = 1.0 / h
        if aspect:
            scalex = min(scalex, scaley)
            scaley = scalex
        node.setScale(scalex, 1, -scaley)
        dimx = w * scalex
        midx = (l * scalex + r * scalex) / 2.0
        dimy = h * scaley
        midy = (top * scaley + bottom * scaley) / 2.0
        node.setPos(-midx + 0.5, 0, midy - 0.5)
