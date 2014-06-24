import libcontext, bee
from bee.segments import *
import spyder, Spyder
from ..models import nodeio
from bee.types import stringtupleparser


class _python_base(bee.worker):
    @classmethod
    def form(cls, f):
        f.code.name = "Python code"
        f.code.type = "pythoncode"

    def place(self):
        raise NotImplementedError("sparta.assessors.python has not been implemented yet")


class python(object):
    """Snippet of custom Python code.
Python assessors may have any number of pull inputs. When the assessor is evaluated (on demand), the values of the inputs is made available to the code, as variables of the same name.
Once the code has executed, the value of the output is determined, based on the syntax mode.
Parameters
(Advanced) output pull type (bool by default)
(Advanced) Syntax mode: "expression", "function" or "generator". "expression" (default) is a single Python expression, "function" uses return, "generator" uses yield.
(Advanced) Advanced input mode: If enabled, inputs must be explicitly pulled using v(), where v is the name of the input."""
    metaguiparams = {
        "inputs": "NodeIOArray",
        "output_type": "str",
        "syntaxmode": "str",
        "advanced": "bool",
        "autocreate": {"inputs": Spyder.NodeIOArray(), "output_type": "bool", "syntaxmode": "expression",
                       "advanced": False},
        "_memberorder": ["syntaxmode", "output_type", "advanced", "inputs"]
    }

    @classmethod
    def form(cls, f):
        f.syntaxmode.name = "Syntax mode"
        f.syntaxmode.type = "option"
        f.syntaxmode.options = "expression", "function", "generator"
        f.syntaxmode.optiontitles = "Expression", "Function", "Generator"
        f.syntaxmode.advanced = True

        f.output_type.name = "Output Type"
        f.output_type.type = "option"
        f.output_type.options = "bool", "int", "float", "(str,identifier)", "(str,action)", "(str,keycode)", "(str,message)", "(str,property)", "(str,process)", "str", "(object,matrix)", "(object,bge)", "object", "custom"
        f.output_type.optiontitles = "Bool", "Integer", "Float", "ID String", "Action String", "Key String", "Message String", "Property String", "Process ID String", "Generic String", "Matrix Object", "BGE Object", "Generic Object", "Custom"
        f.output_type.default = "bool"
        f.output_type.advanced = True

        f.advanced.name = "Advanced Mode"
        f.advanced.advanced = True

        f.inputs.name = "Inputs"
        f.inputs.length = 10
        f.inputs.count_from_one = True
        f.inputs.form = "soft"
        f.inputs.arraymanager = "dynamic"

    def __new__(cls, syntaxmode, output_type, advanced, inputs):
        io_names = set()
        reserved = ("code", "code_parameter_", "outp", "v_outp", "con_outp", "form")
        output_type = stringtupleparser(output_type)

        cls_dict = {
            "code": variable("str"),
            "outp": output("pull", output_type),
            "v_outp": variable(output_type),
            "con_outp": connect("v_outp", "outp")
        }
        cls_dict["code_parameter_"] = parameter(cls_dict["code"], "")
        guiparams = {"outp": {"name": "Output"}}

        # Build set of IO names
        for input_ in inputs:
            if input_.io_name in reserved:
                raise ValueError("Reserved input name: %s" % input_.io_name)

            if input_.io_name in io_names:
                raise ValueError("Duplicate input name: %s" % input_.io_name)

            io_names.add(input_.io_name)

        # Create connections
        for input_ in inputs:
            buffer_name = input_.io_name
            antenna_name = buffer_name + "_"
            type_ = input_.type_

            if type_ == "custom":
                type_ = input_.customtype

            if type_:
                type_ = stringtupleparser(type_)

            cls_dict[antenna_name] = antenna("pull", type_)
            cls_dict[buffer_name] = buffer("pull", type_)
            guiparams[antenna_name] = {"name": buffer_name}

            # Ensure we don't have a name clash with IO names
            connection_name = antenna_name + "connection"
            while connection_name in io_names:
                connection_name += "_"

            cls_dict[connection_name] = connect(antenna_name, buffer_name)

        cls_dict["guiparams"] = guiparams
        return type("python", (_python_base,), cls_dict)
