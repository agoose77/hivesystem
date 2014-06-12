import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
import spyder
from ..models.range_ import IntRange, FloatRange


class random_(object):
    """
    The random sensor contains a random value every tick: it is True or False with a certain probability, or contains a value within a certain range
    
    """
    metaguiparams = {
        "mode": "str",
        "autocreate": {"mode": "bool"},
    }

    @classmethod
    def form(cls, f):
        f.mode.name = "Mode"
        f.mode.advanced = True
        f.mode.type = "option"
        f.mode.options = "bool", "int", "float"
        f.mode.default = "bool"
        f.mode.optiontitles = "True/False", "Integer", "Float"

    def __new__(cls, mode):
        assert mode in ("bool", "int", "float"), mode

        class random_(bee.worker):
            __doc__ = cls.__doc__
            if mode == "bool":
                probability = antenna("pull", "float")
                active = output("pull", "bool")
                is_active = variable("bool")
                connect(is_active, active)
            else:
                if mode == "int":
                    spydermodel = "IntRange"
                else:
                    spydermodel = "FloatRange"
                range_ = antenna("pull", spydermodel)

                random_ = output("pull", mode)
                v_random = variable(mode)
                connect(v_random, random_)

            # Name the inputs and outputs
            guiparams = {
                "probability": {"name": "Probability", "fold": True},
                "range_": {"name": "Range", "fold": True},
                "random_": {"name": "Random"},
                "_memberorder": ["probability", "range_", "random_"],
            }

            # Method to manipulate the parameter form as it appears in the GUI
            @classmethod
            def form(cls, f):
                if mode == "bool":
                    f.probability.default = 0.5
                else:
                    f.range_.default = (0, 0)

            def place(self):
                raise NotImplementedError("sparta.sensors.random_ has not been implemented yet")

        return random_
