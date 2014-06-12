import functools

has_bgl = False
try:
    from bgl import *

    has_bgl = True
except ImportError:
    pass


def draw_grid(sx, sy, linecolor, values):
    glColor4f(*linecolor)
    glBegin(GL_LINES)
    for n in range(sx + 1):
        px = float(n) / sx
        glVertex2f(px, 0.0)
        glVertex2f(px, -1.0)
    for n in range(sy + 1):
        py = float(n) / sy
        glVertex2f(0.0, -py)
        glVertex2f(1.0, -py)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    sizx = 1.0 / sx
    sizy = 1.0 / sy
    counter = 0
    for n in range(sx):
        px = float(n) / sx
        for nn in range(sy):
            py = float(nn) / sy
            if values[counter]:
                glVertex2f(px, -py)
                glVertex2f(px + sizx, -py)
                glVertex2f(px + sizx, -py - sizy)
                glVertex2f(px, -py - sizy)
            counter += 1
    glEnd()


class blenderbgrid(object):
    def __init__(self, canvasdrone, grid, identifier, parameters):
        if not has_bgl: raise ImportError("Cannot import bgl")
        self.grid = grid
        self.parameters = parameters
        self._build_grid()

    def update(self, grid, identifier, parameters):
        self.grid = grid
        self.parameters = parameters
        self._build_grid()

    def remove(self):
        pass

    def _build_grid(self):
        color = getattr(self.parameters, "color", (0, 0, 0, 0))
        sx = self.grid.maxx - self.grid.minx + 1
        sy = self.grid.maxy - self.grid.miny + 1
        values = []
        for n in range(sx):
            for nn in range(sy):
                v = self.grid.get_value(self.grid.minx + n, self.grid.miny + nn)
                values.append(v)
        self.draw = functools.partial(draw_grid, sx, sy, color, values)
