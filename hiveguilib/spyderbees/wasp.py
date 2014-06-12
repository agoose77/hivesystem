class wasp(object):
    metaguiparams = {"spydertype": "type"}

    def __new__(cls, spydertype):
        class wasp(object):
            guiparams = dict(
                __beename__="wasp",
                antennas={},
                outputs={},
                parameters={
                    "val": spydertype,
                    "target": "str",
                    "targetparam": "str",
                },
            )

        return wasp
