"""
Dummy node for bee.segments.transistor in the GUI
"""
class transistor(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    antennas = dict(
      inp = ("pull", type),
      trigger = ("push","trigger"),
    )
    outputs = dict (
      outp = ("push", type),
    )
    params = {
      "triggerfunc": "str"
    }
    class transistor(object):
      guiparams = dict (
        __beename__ = "transistor",
        antennas = antennas,
        outputs = outputs,
        parameters = params,
      )
    return transistor

transistor_int = transistor("int")
transistor_float = transistor("float")
transistor_bool = transistor("bool")
transistor_str = transistor("str")
transistor_id = transistor("id")
