"""
Dummy node for bee.segments.test in the GUI
"""
class test(object):
  guiparams = dict (
    __beename__ = "test",
    antennas = dict(
      inp = ("push", "bool"),
    ),
    outputs = dict (
      outp = ("push", "trigger"),
    ),
    parameters = {},
  )

