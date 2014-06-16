class plugin_mixin_required(object):

    def unfilled(self):
        if self.counter == 0:
            raise TypeError("Plugin needs a socket")


class plugin_mixin_optional(object):

    def unfilled(self):
        pass


class plugin_mixin_single(object):

    def fill(self, socket):
        if self.counter > 0:
            raise TypeError("Plugin can accept only one socket")

        self.__fill__(socket)


class plugin_mixin_multi(object):

    def fill(self, socket):
        self.__fill__(socket)
