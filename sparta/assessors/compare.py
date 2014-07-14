import libcontext, bee
from bee.segments import *
from bee.types import stringtupleparser


class compare(object):

    """The compare assessor compares two input values"""

    metaguiparams = {
        "type_": "str",
        "autocreate": {"type_": "bool"},
    }

    @classmethod
    def form(cls, f):
        f.type_.name = "Type"
        f.type_.type = "option"
        f.type_.options = "bool", "int", "float", "(str,identifier)", "(str,action)", "(str,keycode)", "(str,message)", "(str,property)", "(str,process)", "str", "(object,matrix)", "(object,bge)", "object", "custom"
        f.type_.optiontitles = "Bool", "Integer", "Float", "ID String", "Action String", "Key String", "Message String", "Property String", "Process ID String", "Generic String", "Matrix Object", "BGE Object", "Generic Object", "Custom"
        f.type_.default = "bool"

    def __new__(cls, type_):
        type_ = stringtupleparser(type_)

        class compare(bee.worker):
            __doc__ = cls.__doc__

            # Comparison mode
            mode = variable("str")
            parameter(mode, "equal")

            # Two input values 
            inp1 = antenna("pull", type_)
            inp2 = antenna("pull", type_)
            # One output value returning the result of the comparision
            outp = output("pull", "bool")
            result = variable("bool")
            connect(result, outp)

            # Whenever the result of the comparison is requested..
            # ...pull in the input values...
            b_inp1 = buffer("pull", type_)
            connect(inp1, b_inp1)
            pretrigger(result, b_inp1)
            b_inp2 = buffer("pull", type_)
            connect(inp1, b_inp2)
            pretrigger(result, b_inp2)

            # ...and then compare the values
            @modifier
            def do_compare(self):
                if self.mode == "equal":
                    result = (self.b_inp1 == self.b_inp2)

                elif self.mode == "greater":
                    result = (self.b_inp1 > self.b_inp2)

                elif self.mode == "lesser":
                    result = (self.b_inp1 < self.b_inp2)

                self.result = result

            pretrigger(result, do_compare)

            # Specify names for the comparison mode
            @staticmethod
            def form(f):
                f.mode.name = "Mode"
                f.mode.type = "option"
                f.mode.options = "equal", "greater", "lesser"
                f.mode.optiontitles = "EqualTo", "GreaterThan", "LesserThan"

            guiparams = {
                "inp1": {"name": "Input 1"},
                "inp2": {"name": "Input 2"},
                "outp": {"name": "Output"},
            }

        return compare
