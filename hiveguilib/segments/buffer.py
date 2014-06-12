"""
Dummy nodes for bee.segments.buffer in the GUI
"""


class push_buffer(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        antennas = dict(
            inp=("push", type),
            output=("push", "trigger"),
        )
        outputs = dict(
            outp=("push", type),
            pre_update=("push", "trigger"),
            on_update=("push", "trigger"),
        )
        params = {
            "val": type,
            "is_parameter": "bool",
            "triggerfunc": "str",
        }

        class push_buffer(object):
            guiparams = dict(
                __beename__="push_buffer",
                antennas=antennas,
                outputs=outputs,
                parameters=params,
            )

        return push_buffer


push_buffer_int = push_buffer("int")
push_buffer_float = push_buffer("float")
push_buffer_bool = push_buffer("bool")
push_buffer_str = push_buffer("str")
push_buffer_id = push_buffer("id")


class pull_buffer(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        antennas = dict(
            inp=("pull", type),
            update=("push", "trigger"),
        )
        outputs = dict(
            outp=("pull", type),
            pre_output=("push", "trigger"),
            on_output=("push", "trigger"),
        )
        params = {
            "val": type,
            "is_parameter": "bool",
            "triggerfunc": "str",
        }

        class pull_buffer(object):
            guiparams = dict(
                __beename__="pull_buffer",
                antennas=antennas,
                outputs=outputs,
                parameters=params,
            )

        return pull_buffer


pull_buffer_int = pull_buffer("int")
pull_buffer_float = pull_buffer("float")
pull_buffer_bool = pull_buffer("bool")
pull_buffer_str = pull_buffer("str")
pull_buffer_id = pull_buffer("id")
