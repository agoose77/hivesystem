from ._io_base import io_base
from .. import types
from ._runtime_segment import _runtime_output_push, _runtime_output_pull


class output(io_base):
    def __init__(self, mode, type):
        mt = types.mode_type(mode, type)
        self.mode = mt.mode.value
        self.type = mt.type.value
        self._connection = []
        if self.type in ("trigger", "toggle"):
            self.triggered_input = self.connection_input
            self.triggered_output = self.connection_input
            self.triggered_default = self.connection_input

    def connection_input_type(self):
        return self.mode, self.type

    def connection_input(self, connection):
        if self.mode == "pull" and len(self._connection):
            raise TypeError("Pull output must have only one input")
        self._connection.append(connection)

    def _triggered_input_trigger(self, target, pre=False):
        if pre != False: raise TypeError("push-trigger outputs do not support pre-triggering")
        self._connection.append(target)

    def _triggered_input_(self, target, pre=False):
        self._triggered_input.append((target, pre))

    _triggered_default_ = _triggered_input_

    def guiparams(self, segmentname, guiparams):
        pnam = "outputs"
        if pnam not in guiparams:
            guiparams[pnam] = {}
        p = (self.mode, self.type)
        guiparams[pnam][segmentname] = p

    def build(self, segmentname):
        if self.mode == "push":
            dic = {
                "_connection": self._connection,
                "segmentname": segmentname,
                "type": self.type,
                "istrigger": (self.type in ("trigger", "toggle"))
            }
            return type("runtime_output_push:" + segmentname, (_runtime_output_push,), dic)
        elif self.mode == "pull":
            if self.mode == "pull" and not len(self._connection):
                raise TypeError("Pull output %s must have exactly one input" % (segmentname))
            dic = {
                "_connection": self._connection,
                "segmentname": segmentname,
                "type": self.type,
            }
            return type("runtime_output_pull:" + segmentname, (_runtime_output_pull,), dic)
        else:
            raise ValueError()

    
