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
        "outputtype": "str",
        "syntaxmode": "str",
        "advanced": "bool",
        "autocreate": {"inputs": Spyder.NodeIOArray(), "outputtype": "bool", "syntaxmode": "expression",
                       "advanced": False},
        "_memberorder": ["syntaxmode", "outputtype", "advanced", "inputs"]
    }

    @classmethod
    def form(cls, f):
        f.syntaxmode.name = "Syntax mode"
        f.syntaxmode.type = "option"
        f.syntaxmode.options = "expression", "function", "generator"
        f.syntaxmode.optiontitles = "Expression", "Function", "Generator"
        f.syntaxmode.advanced = True

        f.outputtype.name = "Output Type"
        f.outputtype.type = "option"
        f.outputtype.options = "bool", "int", "float", "(str,identifier)", "(str,action)", "(str,keycode)", "(str,message)", "(str,property)", "(str,process)", "str", "(object,matrix)", "(object,bge)", "object", "custom"
        f.outputtype.optiontitles = "Bool", "Integer", "Float", "ID String", "Action String", "Key String", "Message String", "Property String", "Process ID String", "Generic String", "Matrix Object", "BGE Object", "Generic Object", "Custom"
        f.outputtype.default = "bool"
        f.outputtype.advanced = True

        f.advanced.name = "Advanced Mode"
        f.advanced.advanced = True

        f.inputs.name = "Inputs"
        f.inputs.length = 10
        f.inputs.count_from_one = True
        f.inputs.form = "soft"
        f.inputs.arraymanager = "dynamic"

    def __new__(cls, syntaxmode, outputtype, advanced, inputs):
        ionames = set()
        reserved = ("code", "code_parameter_", "outp", "v_outp", "con_outp", "form")
        outputtype = stringtupleparser(outputtype)
        for inp in inputs:
            if inp.ioname in reserved: raise ValueError("Reserved input name: %s" % inp.ioname)
            if inp.ioname in ionames: raise ValueError("Duplicate input name: %s" % inp.ioname)
            ionames.add(inp.ioname)
        dic = {
            "code": variable("str"),
            "outp": output("pull", outputtype),
            "v_outp": variable(outputtype),
            "con_outp": connect("v_outp", "outp")
        }
        dic["code_parameter_"] = parameter(dic["code"], "")
        guiparams = {}
        guiparams["outp"] = {"name": "Output"}
        counter = 0
        for inp in inputs:
            name = inp.ioname
            name2 = name + "_"
            typ = inp.type_
            if typ == "custom": typ = inp.customtype
            if typ: typ = stringtupleparser(typ)
            dic[name2] = antenna("pull", typ)
            dic[name] = buffer("pull", typ)
            guiparams[name2] = {"name": name}
            while 1:
                counter += 1
                conname = "con" + str(counter)
                if conname not in ionames: break
            dic[conname] = connect(name2, name)

        dic["guiparams"] = guiparams
        return type("python", (_python_base,), dic)
