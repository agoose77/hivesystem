"""
Dummy node for bee.segments.operator in the GUI
"""


class operator(object):
    metaguiparams = {
        "intype": "type",
        "outtype": "type"
    }

    def __new__(cls, intype, outtype):
        antennas = dict(
            inp=("push", intype),
        )
        outputs = dict(
            outp=("push", outtype),
        )
        params = {
        }

        class operator(object):
            guiparams = dict(
                __beename__="operator",
                antennas=antennas,
                outputs=outputs,
                parameters={"code": "pythoncode"},
            )

        return operator

