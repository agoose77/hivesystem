import libcontext, bee
from bee.segments import *
from bee.types import stringtupleparser
import spyder
from ..models.range_ import IntRange, FloatRange


class between(object):
    """
    The between assessor tests if an input value is in between two other values
    """
    metaguiparams = {
        "type_": "str",
        "autocreate": {"type_": "int"},
    }

    @classmethod
    def form(cls, f):
        f.type_.name = "Type"
        f.type_.type = "option"
        f.type_.options = "int", "float"
        f.type_.optiontitles = "Integer", "Float"
        f.type_.default = "int"

    def __new__(cls, type_):
        type_ = stringtupleparser(type_)

        class between(bee.worker):
            __doc__ = cls.__doc__

            # Input values 
            inp = antenna("pull", type_)
            if type_ == "int":
                spydertype = "IntRange"
            elif type_ == "float":
                spydertype = "FloatRange"
            range_ = antenna("pull", spydertype)
            # One output value returning the result of the comparision
            outp = output("pull", "bool")
            result = variable("bool")
            connect(result, outp)

            # Whenever the result of the comparison is requested..
            # ...pull in the input values...
            b_inp = buffer("pull", type_)
            connect(inp, b_inp)
            pretrigger(result, b_inp)
            b_range = buffer("pull", spydertype)
            connect(range_, b_range)
            pretrigger(result, b_range)

            # ...and then compare the values
            @modifier
            def do_compare(self):
                if self.b_inp >= self.b_range.minimum and self.b_inp <= self.b_range.maximum:
                    result = True
                else:
                    result = False
                self.result = result

            pretrigger(result, do_compare)

            guiparams = {
                "inp": {"name": "Input"},
                "range_": {"name": "Range", "fold": True},
                "outp": {"name": "Output"},
            }

        return between
    