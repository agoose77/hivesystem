class attribute(object):
    metaguiparams = {"spydertype": "type"}

    def __new__(cls, spydertype):
        class attribute(object):
            guiparams = dict(
                __beename__="attribute",
                antennas={},
                outputs={},
                parameters={
                    "val": spydertype,
                },
            )

        return attribute
