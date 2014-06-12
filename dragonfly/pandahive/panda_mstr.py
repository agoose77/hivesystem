from .panda_str import panda_str


class panda_mstr(panda_str):
    def __init__(self, canvasdrone, mstr, identifier, parentnode, parameters):
        panda_str.__init__(self, canvasdrone, mstr.value, identifier, parentnode, parameters)

    def update(self, mstr, identifier, parentnode, parameters):
        return panda_str.update(self, mstr.value, identifier, parentnode, parameters)

    def remove(self):
        pass
