import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
import spyder
from ..models.range_ import IntRange, FloatRange
from random import random as rand_float, uniform as rand_range_float, randint as rand_range_int, seed as set_seed

class random_(object):

    """The random sensor contains a random value every tick: it is True or False with a certain probability, or
    contains a value within a certain range"""

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

            seed = antenna("pull", "int")
            seed_buffer = buffer("pull", "int")
            connect(seed, seed_buffer)

            @modifier
            def set_seed_value(self):
                set_seed(self.seed_buffer)

            if mode == "bool":
                probability = antenna("pull", "float")
                probability_buffer = buffer("pull", "float")
                connect(probability, probability_buffer)

                active = output("pull", "bool")
                is_active = variable("bool")
                connect(is_active, active)

                @modifier
                def set_active_random(self):
                    self.is_active = rand_float() < self.probability_buffer

                pretrigger(is_active, probability_buffer)
                trigger(probability_buffer, set_active_random)

            else:
                if mode == "int":
                    spydermodel = "IntRange"
                    @modifier
                    def set_output_random(self):
                        self.v_random = rand_range_int(self.rand_buffer.minumum, self.rand_buffer.maximum)

                else:
                    spydermodel = "FloatRange"
                    @modifier
                    def set_output_random(self):
                        self.v_random = rand_range_float(self.rand_buffer.minumum, self.rand_buffer.maximum)

                range_ = antenna("pull", spydermodel)
                range_buffer = buffer("pull", spydermodel)
                connect(range_, range_buffer)

                random_ = output("pull", mode)
                v_random = variable(mode)
                connect(v_random, random_)

                pretrigger(v_random, seed_buffer)
                pretrigger(v_random, set_seed_value)

                pretrigger(v_random, range_buffer)
                pretrigger(v_random, set_output_random)

            # Name the inputs and outputs
            guiparams = {
                "probability": {"name": "Probability", "fold": True},
                "range_": {"name": "Range", "fold": True},
                "seed": {"name": "Seed", "fold": False, "advanced": True},
                "active": {"name": "Active"},
                "random_": {"name": "Random"},
                "_memberorder": ["probability", "range_", "seed", "active", "random_"],
            }

            # Method to manipulate the parameter form as it appears in the GUI
            @classmethod
            def form(cls, f):
                if mode == "bool":
                    f.probability.default = 0.5

                else:
                    f.range_.default = (0, 0)

            def place(self):
                pass

        return random_
