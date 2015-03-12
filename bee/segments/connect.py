from ._helpersegment import helpersegment
from .. import types


class connect(helpersegment):
    def __init__(self, input, output):
        self.input = types.connection_outputclass(input)
        self.output = types.connection_inputclass(output)
        self.bound = False
        self.identifier = None
        if self.input.bound and self.output.bound:
            self.bound = True
            self.typetest()

    def typetest(self):
        typ1 = self.input.value.connection_output_type()
        typ1 = types.mode_type(*typ1)
        typ2 = self.output.value.connection_input_type()
        typ2 = types.mode_type(*typ2)
        if typ1.mode.value != typ2.mode.value or not types.typecompare(typ1.type.value, typ2.type.value):
            raise TypeError("Mismatch between input and Output types: (%s, %s) and (%s, %s)" % \
                            (typ1.mode.value, typ1.type.value, typ2.mode.value, typ2.type.value))

    def bind(self, classname, dic):
        if not self.bound:
            self.input.bind(classname, dic)
            self.output.bind(classname, dic)
            self.bound = True
            self.typetest()

    def connect(self, identifier):
        self.identifier = identifier
        self.input.value.connection_output(self)
        self.output.value.connection_input(self)
