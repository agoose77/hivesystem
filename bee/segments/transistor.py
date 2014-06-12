from .. import types
from ._runtime_segment import _runtime_segment
import libcontext


class runtime_transistor(_runtime_segment):
    startvalue = None

    def __init__(self, beeinstance, beename):
        self.value = self.startvalue
        _runtime_segment.__init__(self, "pull", "push", beeinstance, beename)

    def input(self, value):
        self.value = value

    def update(self):
        value = self.pull_input()
        self.input(value)
        for target in self.push_outputs: target(value)

    def output(self):
        if self.value == None: raise ValueError("Transistor segment cannot push None")
        return self.value


class transistor(object):
    def __init__(self, type):
        self.type = types.typeclass(type)
        if self.type.push_type:
            raise TypeError("Push-specific type %s cannot be used with transistors" % self.type.value)
        self.type = self.type.value
        self._connection_input = []
        self._connection_output = []
        self._triggered_input = []
        self._triggered_output = []
        self._triggered_update = []
        self.startvalue = None

    def connection_input_type(self):
        return "pull", self.type

    def connection_input(self, connection):
        if len(self._connection_input):
            raise AttributeError("Transistors can have only a single input")
        self._connection_input.append(connection)

    def connection_output_type(self):
        return "push", self.type

    def connection_output(self, connection):
        self._connection_output.append(connection)

    def set_startvalue(self, value):
        self.startvalue = value

    def triggered_input(self, arg):
        self._triggered_input.append(arg)

    def triggered_output(self, arg):
        self._triggered_output.append(arg)

    def triggered_update(self, arg):
        self._triggered_update.append(arg)

    triggered_default = triggered_update

    def build(self, segmentname):
        dic = {
            "startvalue": self.startvalue,
            "segmentname": segmentname,
            "connection_input": self._connection_input,
            "connection_output": self._connection_output,
            "_triggered_input": self._triggered_input,
            "_triggered_output": self._triggered_output,
            "_triggered_update": self._triggered_update,
        }
        return type("runtime_transistor:" + segmentname, (runtime_transistor,), dic)
  
