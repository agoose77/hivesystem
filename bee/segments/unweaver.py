from .. import types
from ._runtime_segment import runtime_unweaver


class unweaver(object):
    def __init__(self, type, *outputs):
        self.type = types.typeclass(type).get_tuple()
        if len(self.type) != len(outputs):
            raise TypeError("Unweaver is declared as a tuple of %d outputs, but was initialized with only %d" % (
            len(self.type), len(outputs)))
        self.outputs = []
        for outp in outputs:
            self.outputs.append(types.connection_inputclass(outp))
        self._connection_input = []

        self.bound = True
        for outp in self.outputs:
            if not outp.bound:
                self.bound = False
                break
        self.typetest()

    def typetest(self):
        for outp, typ in zip(self.outputs, self.type):
            if not outp.bound: continue
            refetyp = types.mode_type("push", typ)
            outptyp = outp.value.connection_input_type()
            outptyp = types.mode_type(*outptyp)
            if outptyp != refetyp:
                raise TypeError("Unweaver output type should be (%s, %s), is (%s, %s)" % \
                                (refetyp.mode.value, refetyp.type.value, outptyp.mode.value, outptyp.type.value))

    def bind(self, classname, dic):
        if not self.bound:
            for outp in self.outputs:
                if not outp.bound: outp.bind(classname, dic)
            self.bound = True
            self.typetest()

    def connection_input_type(self):
        return "push", self.type

    def connection_input(self, connection):
        self._connection_input.append(connection)

    def connect(self, identifier):
        class unweaver_proxy:
            def __init__(self, identifier):
                self.identifier = identifier

        self.identifier = "unweaver-" + identifier
        for onr, outp in enumerate(self.outputs):
            outp.value.connection_input(unweaver_proxy(self.identifier + ":" + str(onr + 1)))

    def build(self, segmentname):
        dic = {
            "segmentname": segmentname,
            "identifier": self.identifier,
            "_outputs": self.outputs,
            "connection_input": self._connection_input,
        }
        return type("runtime_unweaver:" + segmentname, (runtime_unweaver,), dic)
