from .. import types
from ._helpersegment import helpersegment


class trigger(helpersegment):
    pre = False

    def __init__(self, input, output, mode_input="default", mode_output="default"):
        self.input = types.triggering_class(input, mode_input, self.pre)
        self.output = types.triggered_class(output, mode_output)
        self.bound = False
        if self.input.bound and self.output.bound:
            self.bound = True

    def bind(self, classname, dic):
        if not self.bound:
            self.input.bind(classname, dic)
            self.output.bind(classname, dic)
            self.bound = True

    def connect(self, identifier):
        self.identifier = identifier
        attr = "triggering_" + self.input.mode
        getattr(self.input.value, attr)((self, self.pre))
        attr = "triggered_" + self.output.mode
        getattr(self.output.value, attr)(self)
    
