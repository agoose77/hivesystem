has_bgl = False
try:
    from bgl import *
    import blf

    has_bgl = True
except ImportError:
    pass


class blender_str(object):
    def __init__(self, canvasdrone, string, identifier, parameters):
        if not has_bgl: raise ImportError("Cannot import bgl")
        self.text = string
        self.parameters = parameters
        self._scale()

    def update(self, string, identifier, parameters):
        self.text = string
        self.parameters = parameters
        self._scale()

    def remove(self):
        pass

    def _scale(self):
        self.aspect = True
        if hasattr(self.parameters, "aspect"):
            self.aspect = self.parameters.aspect

        blf.size(0, 100, 72)
        w, h = blf.dimensions(0, self.text)
        # add a little margin...
        margin = 55
        w += margin;
        h += margin

        scalex = 0
        if w > 0: scalex = 1.0 / w
        scaley = 0
        if h > 0: scaley = 1.0 / h
        if self.aspect:
            scalex = min(scalex, scaley)
            scaley = scalex
        self.scale = (scalex, scaley, 1)
        self.pos = (0.5 - 0.5 * (w - margin) * scalex, -0.5 * (h - margin) * scaley, 0)

    def draw(self):
        glColor3f(1, 1, 1)
        glPushMatrix()
        glTranslatef(*self.pos)
        glScalef(*self.scale)
        txt = self.text
        blf.position(0, 0, 0, 0)
        glScalef(1, -1, -1)
        blf.size(0, 100, 72)
        blf.draw(0, txt.replace('\t', '    '))
        glPopMatrix()
