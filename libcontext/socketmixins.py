class socket_mixin_single(object):
    def fill(self, *args, **kargs):
        if self.counter > 0: raise TypeError("Socket can accept only one plugin")
        self.__fill__(*args, **kargs)


class socket_mixin_multi(object):
    def fill(self, *args, **kargs):
        self.__fill__(*args, **kargs)


class socket_mixin_required(object):
    def unfilled(self):
        if self.counter == 0: raise TypeError("Socket must be filled")


class socket_mixin_optional(object):
    def unfilled(self):
        pass

