import bee

import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from .bglnode import bgl_pixelnode, bgl_aspectnode, bgl_rendernode

has_bgl = False
try:
    from bgl import *

    has_bgl = True
except ImportError:
    pass


class animation(object):
    def __init__(self,
                 name,
                 start,
                 end,
                 layer=0,
                 priority=0,
                 blendin=0.0,
                 play_mode="play",
                 layer_weight=0.0,
                 ipo_flags=0,
                 speed=1.0
    ):
        self.name = name
        self.start = start
        self.end = end
        self.layer = layer
        self.priority = priority
        self.blendin = blendin
        assert play_mode in ("play", "loop", "ping_pong", "pingpong")
        self.play_mode = play_mode
        self.layer_weight = layer_weight
        self.ipo_flags = ipo_flags
        self.speed = speed


class cameraloader(bee.drone):
    """
    sets the first camera object in the scene as camera
    """

    def load(self, scene):
        self.camera = scene.active_camera
        return []

    def get_camera(self):
        assert self.camera is not None, "Blender scene contains no camera"
        return self.camera

    def get_camera_matrix(self):
        from ..scene.matrix import matrix

        return matrix(self.get_camera(), "Blender")

    def place(self):
        libcontext.plugin("get_camera", plugin_supplier(self.get_camera))
        libcontext.plugin(("blender", "camera"), plugin_supplier(self.get_camera))
        libcontext.plugin("camera", plugin_supplier(self.get_camera_matrix))
        libcontext.plugin(("camera", "Blender"), plugin_supplier(self.get_camera))

        libcontext.plugin(("blender", "sceneloader"), plugin_single_required(self.load))


class entityclassloader(bee.drone):
    """
    registers all objects on the inactive layer as entity classes
    """

    def load(self, scene):
        processed = []
        for obj in scene.objectsInactive:
            self.register((obj.name, obj, obj.worldTransform))
            processed.append(obj.name)
        return processed

    def set_register(self, register):
        self.register = register

    def place(self):
        libcontext.plugin(("blender", "sceneloader"), plugin_single_required(self.load))
        libcontext.socket(("blender", "entityclass-register"), socket_single_required(self.set_register))


class entityloader(bee.drone):

    def load(self, obj):
        self.register((obj.name, obj))

    def set_register(self, register):
        self.register = register

    def place(self):
        libcontext.socket(("blender", "entity-register"), socket_single_required(self.set_register))
        libcontext.plugin(("blender", "objectloader"), plugin_single_required(self.load))


class animationloader(bee.drone):
    def __init__(self):
        self.animations = []

    # this function is meant to be configured from Python;
    # later, perhaps extract data from scene
    def add_animation(self, animation_name, anim):
        assert isinstance(anim, animation)
        self.animations.append((animation_name, anim))

    def load(self, scene):
        #ignore scene for now, extract animations from Python
        for animation_name, anim in self.animations:
            self.register(animation_name, anim)
        return []

    def set_register(self, register):
        self.register = register

    def place(self):
        libcontext.socket(("blender", "animation-register"), socket_single_required(self.set_register))
        libcontext.plugin(("blender", "sceneloader"), plugin_single_required(self.load))


class blenderscene(bee.drone):
    """
    Registers the objects in the scene with the blenderhive

    The blenderscene can take two kind of plugins:
    - Scene loaders take the whole scene and return a list of processed object names
    - Object loaders take a single object; the return value

    All loaders are called in reverse order:
     first the scene loaders, then the object loaders
    Object loaders are only called on unprocessed objects

    """

    def __init__(self):
        self.sceneloaders = []
        self.objectloaders = []
        self.pixel2d = bgl_pixelnode()
        self.render2d = bgl_rendernode()
        self.aspect2d = bgl_aspectnode()
        self._loaded = False
        self._textures_to_load = []

    def add_sceneloader(self, sceneloader):
        self.sceneloaders.append(sceneloader)

    def add_objectloader(self, objectloader):
        self.objectloaders.append(objectloader)

    def load(self):
        processed = set()
        scene = self.scene()
        names = [obj.name for obj in scene.objects + scene.objectsInactive]
        for l in reversed(self.sceneloaders):
            proc = l(scene)
            for p in proc:
                assert p in names, p
                processed.add(p)
        for l in reversed(self.objectloaders):
            for obj in scene.objects:
                if obj.name not in processed:
                    proc = l(obj)
                    if proc: processed.add(obj.name)
        self._load_textures()
        scene.post_draw = [self.pixel2d.draw, self.aspect2d.draw, self.render2d.draw]
        self._loaded = True

    @staticmethod
    def _load_texture(tex_id, im_buf, size):
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            size[0], size[1], 0,
            GL_RGBA, GL_UNSIGNED_BYTE, im_buf
        )

    def _load_textures(self):
        assert has_bgl
        if not len(self._textures_to_load): return
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        for tex_id, im_buf, size in self._textures_to_load:
            self._load_texture(tex_id, im_buf, size)
        self._textures_to_load = []

    def _textureloader(self, tex_id, im_buf, size):
        if self._loaded:  # immediate mode
            self._load_texture(tex_id, im_buf, size)
        else:  # we aren't initialized yet; queue up the load command
            self._textures_to_load.append((tex_id, im_buf, size))

    def set_scene(self, scene):
        self.scene = scene

    def place(self):
        libcontext.plugin("startupfunction", plugin_single_required((self.load, 1)))
        libcontext.socket(("blender", "scene"), socket_single_required(self.set_scene))

        libcontext.socket(("blender", "sceneloader"), socket_container(self.add_sceneloader))
        libcontext.socket(("blender", "objectloader"), socket_container(self.add_objectloader))

        libcontext.plugin(("blender", "noderoot", "render2d"), plugin_supplier(lambda: self.render2d))
        libcontext.plugin(("blender", "noderoot", "aspect2d"), plugin_supplier(lambda: self.aspect2d))
        libcontext.plugin(("blender", "noderoot", "pixel2d"), plugin_supplier(lambda: self.pixel2d))

        libcontext.plugin("textureloader", plugin_supplier(self._textureloader))

