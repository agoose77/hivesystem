import libcontext, bee
from bee.segments import *


class not_(bee.worker):
    """
    The not assessor returns True if its input is False
    """

    outp = output("pull", "bool")
    inp = antenna("pull", "bool")

    b_inp = buffer("pull", "bool")

    v_outp = variable("bool")
    connect(v_outp, outp)

    # Evaluation function
    @modifier
    def evaluate(self):
        self.v_outp = not self.b_inp

    # Whenever the output is requested: update the inputs and evaluate
    pretrigger(v_outp, b_inp)
    pretrigger(v_outp, evaluate)

    # Name the inputs and outputs
    guiparams = {
        "outp": {"name": "Output"},
        "inp": {"name": "Input", "foldable": False},
    }
    