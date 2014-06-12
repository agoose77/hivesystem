"""
Dummy node for bee.segments.variable in the GUI
"""


class variable(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        antennas = dict(
            inp=("push", type),
        )
        outputs = dict(
            outp=("pull", type),
            pre_update=("push", "trigger"),
            pre_output=("push", "trigger"),
            on_update=("push", "trigger"),
            on_output=("push", "trigger"),
        )
        params = {
            "val": type,
            "is_parameter": "bool",
        }

        class variable(object):
            guiparams = dict(
                __beename__="variable",
                antennas=antennas,
                outputs=outputs,
                parameters=params,
            )

        return variable


variable_int = variable("int")
variable_float = variable("float")
variable_bool = variable("bool")
variable_str = variable("str")
variable_id = variable("id")

