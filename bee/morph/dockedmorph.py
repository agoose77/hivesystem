class dockedmorph(object):
    def __init__(self, morph, mediator, inputs, outputs):
        self.was_active = morph.active
        self.morph = morph
        self.morph.active = False
        self.mediator = mediator
        self.inputs = dockedmorph_inputs(morph, inputs)
        self.outputs = dockedmorph_outputs(morph, outputs)

    def run(self):
        self.morph.run()

    def undock(self):
        self.morph.active = self.was_active


class dockedmorph_inputs(object):
    def __init__(self, morph, inputs):
        self._inputs = inputs
        self._morph = morph

    def __setitem__(self, item, value):
        self._inputs[item].value = value


class dockedmorph_outputs(object):
    def __init__(self, morph, outputs):
        self._outputs = outputs
        self._morph = morph

    def __getitem__(self, item):
        return self._outputs[item].value
    
