"""
Dummy nodes for bee.segments.antenna in the GUI
"""
class push_antenna(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    antennas = dict(
    )
    outputs = dict (
      outp = ("push", type),
    )
    params = dict (
    )
    class push_antenna(object):
      guiparams = dict (
        __beename__ = "push_antenna",
        antennas = antennas,
        outputs = outputs,
        parameters = params,
      )
    return push_antenna

push_antenna_trigger = push_antenna("trigger")
push_antenna_int = push_antenna("int")
push_antenna_float = push_antenna("float")
push_antenna_bool = push_antenna("bool")
push_antenna_str = push_antenna("str")
push_antenna_id = push_antenna("id")

class pull_antenna(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    antennas = dict(
    )
    outputs = dict (
      outp = ("pull", type),
    )
    params = dict (
    )
    class pull_antenna(object):
      guiparams = dict (
        __beename__ = "pull_antenna",
        antennas = antennas,
        outputs = outputs,
        parameters = params,
      )
    return pull_antenna

pull_antenna_int = pull_antenna("int")
pull_antenna_float = pull_antenna("float")
pull_antenna_bool = pull_antenna("bool")
pull_antenna_str = pull_antenna("str")
pull_antenna_id = pull_antenna("id")
