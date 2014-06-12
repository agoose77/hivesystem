from .. import types
from ._helpersegment import helpersegment
from ._runtime_segment import _runtime_init


class init(helpersegment):
    def __init__(self, target, mode="default"):
        self.target = types.triggered_class(target, mode)
        self.bound = self.target.bound

    def bind(self, classname, dic):
        if not self.bound:
            self.target.bind(classname, dic)

    def connect(self, identifier):
        self.identifier = str(identifier)
        attr = "triggered_" + self.target.mode
        getattr(self.target.value, attr)(self)

    def build(self, segmentname):
        assert str(segmentname) == self.identifier
        return type("runtime_init:" + str(segmentname), (_runtime_init,), {"segmentname": str(segmentname)})
