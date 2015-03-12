from .. import types
from ._runtime_segment import runtime_untoggler


class untoggler(object):
    def __init__(self, output1, output2):
        self.output1 = types.connection_inputclass(output1)
        self.output2 = types.connection_inputclass(output2)
        self._connection_input = []

        self.bound = (self.output1.bound and self.output2.bound)
        self.typetest()

    def typetest(self):
        if self.output1.bound:
            outptyp = self.output1.value.connection_input_type()
            outptyp = types.mode_type(*outptyp)
            if outptyp != types.mode_type("push", "trigger"):
                raise TypeError('Untoggler Output 1 should be of type ("push", "trigger"), is (%s, %s)' % \
                                (outptyp.mode.value, outptyp.type.value))

        if self.output2.bound:
            outptyp = self.output2.value.connection_input_type()
            outptyp = types.mode_type(*outptyp)
            if outptyp != types.mode_type("push", "trigger"):
                raise TypeError('Untoggler Output 2 should be of type ("push", "trigger"), is (%s, %s)' % \
                                (outptyp.mode.value, outptyp.type.value))

    def bind(self, classname, dic):
        if not self.bound:
            if not self.output1.bound: self.output1.bind(classname, dic)
            if not self.output2.bound: self.output2.bind(classname, dic)
            self.bound = True
            self.typetest()

    def connection_input_type(self):
        return "push", "toggle"

    def connection_input(self, connection):
        self._connection_input.append(connection)

    def connect(self, identifier):
        class untoggler_proxy:
            def __init__(self, identifier):
                self.identifier = identifier

        self.identifier = "untoggler-" + identifier
        self.output1.value.connection_input(untoggler_proxy(self.identifier + ":1"))
        self.output2.value.connection_input(untoggler_proxy(self.identifier + ":2"))

    def build(self, segmentname):
        dic = {
            "segmentname": segmentname,
            "identifier": self.identifier,
            "_output1": self.output1,
            "_output2": self.output2,
            "connection_input": self._connection_input,
        }
        return type("runtime_untoggler:" + segmentname, (runtime_untoggler,), dic)
