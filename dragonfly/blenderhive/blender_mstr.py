from .blender_str import blender_str


class blender_mstr(blender_str):
    def __init__(self, canvasdrone, mstr, identifier, parameters):
        blender_str.__init__(self, canvasdrone, mstr.value, identifier, parameters)

    def update(self, mstr, identifier, parameters):
        return blender_str.update(self, mstr.value, identifier, parameters)

    def remove(self):
        pass
