from .. import types
from ._runtime_segment import _runtime_operator


class operator(object):
    def __init__(self, callback, inptype, outptype):
        self.callback = callback

        if isinstance(self.callback, str):
            self.bound = False

        else:
            self.bound = True
            if not hasattr(self.callback, "__call__"):
                raise TypeError("Operator must have a callable object")

        self.inptype = types.typeclass(inptype)
        self.outptype = types.typeclass(outptype)
        self._connection_input = []
        self._connection_output = []

    def test_callable(self):
        if not self.bound:
            nam = self.callback
            if not hasattr(self, nam):
                raise AttributeError("Operator has no method %s" % nam)

            self.callback = getattr(self, nam)
            if not hasattr(self.callback, "__call__"):
                raise TypeError("Operator must have a callable object, and attribute %s is not callable" % nam)

            self.bound = True

    def connection_input_type(self):
        return "push", self.inptype

    def connection_input(self, connection):
        self._connection_input.append(connection)

    def connection_output_type(self):
        return "push", self.outptype

    def connection_output(self, connection):
        self._connection_output.append(connection)

    def build(self, segmentname):
        if (isinstance(self.inptype.value, tuple)):
            intuple = True

        else:
            intuple = False

        dic = {
            "_connection_input": self._connection_input,
            "_connection_output": self._connection_output,
            "segmentname": segmentname,
            "callback": (self.callback,),
            "intuple": intuple
        }
        return type("runtime_operator:" + segmentname, (_runtime_operator,), dic)
