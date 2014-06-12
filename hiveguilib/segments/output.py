"""
Dummy node for bee.segments.output in the GUI
"""


class push_output(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        antennas = dict(
            inp=("push", type),
        )
        outputs = dict(
        )
        params = dict(
        )
        if type == "trigger": params["triggerfunc"] = "str"

        class push_output(object):
            guiparams = dict(
                __beename__="push_output",
                antennas=antennas,
                outputs=outputs,
                parameters=params,
            )

        return push_output


push_output_int = push_output("int")
push_output_float = push_output("float")
push_output_bool = push_output("bool")
push_output_str = push_output("str")
push_output_id = push_output("id")


class pull_output(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        antennas = dict(
            inp=("pull", type),
        )
        outputs = dict(
        )
        params = dict(
        )

        class pull_output(object):
            guiparams = dict(
                __beename__="pull_output",
                antennas=antennas,
                outputs=outputs,
                parameters=params,
            )

        return pull_output


pull_output_int = pull_output("int")
pull_output_float = pull_output("float")
pull_output_bool = pull_output("bool")
pull_output_str = pull_output("str")
pull_output_id = pull_output("id")
