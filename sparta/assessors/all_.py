import libcontext, bee
from bee.segments import *


class all_(bee.worker):
    """
    The all assessor returns True if all of its inputs are True
    """

    outp = output("pull", "bool")
    inp1 = antenna("pull", "bool")
    inp2 = antenna("pull", "bool")
    inp3 = antenna("pull", "bool")
    inp4 = antenna("pull", "bool")

    b_inp1 = buffer("pull", "bool")
    b_inp2 = buffer("pull", "bool")
    b_inp3 = buffer("pull", "bool")
    b_inp4 = buffer("pull", "bool")
    connect(inp1, b_inp1)
    connect(inp2, b_inp2)
    connect(inp3, b_inp3)
    connect(inp4, b_inp4)

    v_outp = variable("bool")
    connect(v_outp, outp)

    # Evaluation function
    @modifier
    def evaluate(self):
        outp = False
        if self.b_inp1 and self.b_inp2 and self.b_inp3 and self.b_inp4: outp = True
        self.v_outp = outp

    # Whenever the output is requested: update the inputs and evaluate
    pretrigger(v_outp, b_inp1)
    pretrigger(v_outp, b_inp2)
    pretrigger(v_outp, b_inp3)
    pretrigger(v_outp, b_inp4)
    pretrigger(v_outp, evaluate)

    # Name the inputs and outputs
    guiparams = {
        "outp": {"name": "Output"},
        "inp1": {"name": "Input 1", "foldable": False},
        "inp2": {"name": "Input 2"},
        "inp3": {"name": "Input 3", "fold": True},
        "inp4": {"name": "Input 4", "fold": True},
    }

    # Method to manipulate the parameter form as it appears in the GUI
    @classmethod
    def form(cls, f):
        f.inp1.default = True
        f.inp2.default = True
        f.inp3.default = True
        f.inp4.default = True
