import libcontext
from bee.bind import *


class bind(bind_baseclass):
    bind_gameobject = bindparameter(True)
    binder("bind_gameobject", True, pluginbridge(("entity", "get", "Blender")))
