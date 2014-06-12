from bee.types import boolparser


class wasp(object):
    guiparams = dict(
        __beename__="wasp",
        antennas={},
        outputs={},
        parameters={
            "injected": "str",
            "target_name": "str",
            "target_parameter": "str",
            "sting": ("bool", False),
            "accumulate": ("bool", False),
        },
    )
