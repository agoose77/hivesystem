"""
Dummy node for bee.segments.modifier in the GUI
"""


class modifier(object):
    guiparams = dict(
        __beename__="modifier",
        antennas=dict(
            trigger=("push", "trigger"),
        ),
        outputs=dict(
            on_trigger=("push", "trigger"),
            pre_trigger=("push", "trigger"),
        ),
        parameters={"code": "pythoncode"},
    )

