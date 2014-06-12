from .beewrapper import reg_beehelper

from . import myobject


class attribute(myobject):
    __metaclass__ = reg_beehelper

    def __init__(self, *args):
        for a in args:
            if not isinstance(a, str) and not isinstance(a, int):
                raise TypeError("bee.attribute must be called with string (attribute) and/or int (index) argument(s)")
        self.args = args
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent

    def __call__(self, parent=None, prebuild=False):
        if prebuild == True:
            if self.parent is None: return self
            if parent is not None and parent is not self.parent: return self
        if self.parent is None: raise ValueError(
            "bee.attribute('%s') doesn't know its parent hive, please place it as a named bee inside a hive" % str(
                self.args))
        if len(self.args) == 0: return self.parent
        if self.args[0] == "__call__":
            ret = self.parent()
        else:
            a = self.args[0]
            if isinstance(a, int):
                ret = self.parent[a]
            else:
                ret = getattr(self.parent, a)
        for a in self.args[1:]:
            if a == "__call__":
                ret = ret()
            else:
                if isinstance(a, int):
                    ret = ret[a]
                else:
                    ret = getattr(ret, a)
        return ret
