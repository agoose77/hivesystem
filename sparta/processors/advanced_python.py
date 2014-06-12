import libcontext, bee
from bee.segments import *
import spyder, Spyder
from ..models import nodeio
from bee.types import stringtupleparser


class _advanced_python_base(bee.worker):
    @classmethod
    def form(cls, f):
        f.code.name = "Python code"
        f.code.type = "pythoncode"
        f.persistent.name = "Persistent"
        f.persistent.tooltip = "Output values persist between invocations"
        f.push_activates.name = "Activates on push"
        f.push_activates.tooltip = "Whenever a push input is triggered, the processor activates"
        f.pull_activates.name = "Activates on pull"
        f.pull_activates.tooltip = "Whenever a pull output is requested, the processor activates"
        f.memberorder = "persistent", "push_activates", "pull_activates", "code"

    def place(self):
        raise NotImplementedError("sparta.processors.advanced_python has not been implemented yet")


class advanced_python(object):
    """A snippet of advanced custom Python code.
Activated by trigger. Can have any number of inputs and outputs, which can be push, pull or trigger.
When the Python processor is activated, all push inputs are evaluated, and made available to the code as variables of the same name.
Push inputs that have not been set since the previous invocation are set to None, unless the processor is persistent.
Within the code, a pull input's value must be explicitly requested using v(), where v is the name of the pull input
Within the code, a push output must be explicitly firedusing v(), where v is the name of the push output
After the code has run, its locals() are inspected for pull output variables. All pull output variables must be set (unless persistent).

Parameters:
Persistent: if True, all push inputs and pull outputs have persistent values from one invocation to the next.
Activate by push: if True, every change on a push input triggers the execution of the controller.
Activate by pull: if True, every value request on a pull output (pre-)triggers the execution of the controller
"""
    metaguiparams = {
        "inputs": "AdvancedNodeIOArray",
        "outputs": "AdvancedNodeIOArray",
        "autocreate": {"inputs": Spyder.AdvancedNodeIOArray(), "outputs": Spyder.AdvancedNodeIOArray()},
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
        reserved = ("trig", "code", "code_parameter_",
                    "persistent", "persistent_parameter_",
                    "push_activates", "push_activates_parameter_",
                    "pull_activates", "pull_activates_parameter_",
                    "form"
        )
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
            "push_activates": variable("bool"),
            "pull_activates": variable("bool"),
        }
        dic["code_parameter_"] = parameter(dic["code"], "")
        dic["persistent_parameter_"] = parameter(dic["persistent"], False)
        dic["push_activates_parameter_"] = parameter(dic["push_activates"], False)
        dic["pull_activates_parameter_"] = parameter(dic["pull_activates"], False)
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
        return type("advanced_python", (_advanced_python_base,), dic)
