import functools

has_bgl = False
try:
    from bgl import *

    has_bgl = True
except ImportError:
    pass


def draw_image(tex_id, color, texco, transparency):
    glEnable(GL_TEXTURE_2D)

    if transparency:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor4f(*color)

    glBegin(GL_QUADS)
    positions = [(0, 0), (1, 0), (1, -1), (0, -1)]
    for tex, pos in zip(texco, positions):
        glTexCoord2f(tex[0], tex[1])
        glVertex2f(pos[0], pos[1])
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)

    if transparency:
        glDisable(GL_BLEND)

    glDisable(GL_TEXTURE_2D)


import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class canvasdrone_baseclass(object):
    def _set_textureloader(self, textureloader):
        self.textureloader = textureloader

    def place(self):
        libcontext.socket("textureloader", socket_single_required(self._set_textureloader))


class blenderimage(object):
    def __init__(self, canvasdrone, imagefile, identifier, parameters):
        if not has_bgl: raise ImportError("Cannot import bgl")
        self.image = None
        self.identifier = identifier
        self.imagefile = imagefile
        self.parameters = parameters
        self.textureloader = canvasdrone.textureloader

        id_buf = Buffer(GL_INT, 1)
        # KLUDGE: glGenTextures does not work on Windows before BGE has been fired up
        #glGenTextures(1, id_buf)
        #self.tex_id = id_buf.to_list()[0] if hasattr(id_buf, "to_list") else id_buf.list[0]
        import random

        self.tex_id = random.randint(1, 99999)
        self.update_image()

    def update(self, imagefile, identifier, parameters):
        self.imagefile = imagefile
        self.parameters = parameters
        if imagefile != self.imagefile:
            self.imagefile = imagefile
            self.update_image()

    def remove(self):
        self._delete_texture()

    def update_image(self):
        import bge

        texco0 = [(0, 0), (1, 0), (1, 1), (0, 1)]
        texco = getattr(self.parameters, "texco", texco0)
        transparency = getattr(self.parameters, "transparency", False)
        color = getattr(self.parameters, "color", (1, 1, 1, 1))

        self.image = bge.texture.ImageFFmpeg(self.imagefile)
        self.image.scale = False
        if self.image.image is None: raise ValueError(self.imagefile)

        self.textureloader(self.tex_id, self.image.image, self.image.size)

        self.draw = functools.partial(
            draw_image,
            self.tex_id,
            color,
            texco,
            transparency
        )

    def _delete_texture(self):
        if self.image is None: return
        self.image = None
        id_buf = Buffer(GL_INT, 1)
        id_buf[0] = self.tex_id
        glDeleteTextures(1, id_buf)

    def __del__(self):
        self._delete_texture()

