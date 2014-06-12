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
        f.persistent.name = "Persistent"
        f.persistent.tooltip = "Output values persist between invocations"
        f.memberorder = "persistent", "code"

    def place(self):
        raise NotImplementedError("sparta.processors.python has not been implemented yet")


class python(object):
    """A snippet of custom Python code.
Activated by trigger. Can have any number of pull inputs and any number of outputs, which can be push, pull or trigger.
When the Python processor is activated, all inputs are pulled in, and made available to the code as variables of the same name.
If persistent, previous pull output values are likewise added.
After the code has run, its locals() are inspected for output variables.
All pull output variables must be set (unless persistent).
If a push output variable has been set, it is fired towards its targets when the processor has finished.
If a trigger output variable has been set to True, it is fired towards its targets when the processor has finished"""
    metaguiparams = {
        "inputs": "NodeIOArray",
        "outputs": "AdvancedNodeIOArray",
        "autocreate": {"inputs": Spyder.NodeIOArray(), "outputs": Spyder.AdvancedNodeIOArray()},
    }

    @classmethod
    def form(cls, f):
        f.inputs.name = "Inputs"
        f.inputs.length = 10
        f.inputs.count_from_one = True
        f.inputs.form = "soft"
        f.inputs.arraymanager = "dynamic"

        f.outputs.name = "Outputs"
        f.outputs.length = 10
        f.outputs.count_from_one = True
        f.outputs.form = "soft"
        f.outputs.arraymanager = "dynamic"

    def __new__(cls, inputs, outputs):
        ionames = set()
        reserved = ("trig", "code", "code_parameter_", "persistent", "persistent_parameter_", "form")
        for inp in inputs:
            if inp.ioname in reserved: raise ValueError("Reserved input name: %s" % inp.ioname)
            if inp.ioname in ionames: raise ValueError("Duplicate input name: %s" % inp.ioname)
            ionames.add(inp.ioname)
        for outp in outputs:
            if outp.ioname in reserved: raise ValueError("Reserved output name: %s" % outp.ioname)
            if outp.ioname in ionames: raise ValueError("Duplicate input/output name: %s" % outp.ioname)
            ionames.add(outp.ioname)
        dic = {
            "trig": antenna("push", "trigger"),
            "code": variable("str"),
            "persistent": variable("bool"),
        }
        dic["code_parameter_"] = parameter(dic["code"], "")
        dic["persistent_parameter_"] = parameter(dic["persistent"], False)
        guiparams = {}
        guiparams["trig"] = {"name": "Trigger"}
        guiparams["_memberorder"] = ["trig"]
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

        for outp in outputs:
            name = outp.ioname
            name2 = name + "_"
            typ = outp.type_
            guiparams[name2] = {"name": name}
            if typ == "custom": typ = outp.customtype
            if typ: typ = stringtupleparser(typ)
            if outp.mode == "trigger":
                dic[name2] = output("push", "trigger")
                dic[name2 + "trig_"] = triggerfunc(dic[name2])
                dic[name] = variable("bool")
            else:
                dic[name2] = output(outp.mode, typ)
                dic[name] = buffer(outp.mode, typ)
                while 1:
                    counter += 1
                    conname = "con" + str(counter)
                    if conname not in ionames: break
                dic[conname] = connect(name, name2)

        dic["guiparams"] = guiparams
        return type("python", (_python_base,), dic)
