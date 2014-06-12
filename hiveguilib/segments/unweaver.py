"""
Dummy node for bee.segments.unweaver in the GUI
"""
class unweaver(object):
  metaguiparams = {
   "type1":"type",
   "type2":"type",
   "type3":"type",
   "type4":"type",
   "type5":"type",
   "type6":"type",
   "type7":"type",
   "type8":"type",
   "type9":"type",
  }
  def __new__(cls, *types, **kwtypes):
    ktypes = [v[1] for v in sorted(kwtypes.items())]
    alltypes = list(types) + list(ktypes)
    types = tuple([t for t in alltypes if t is not None and len(t) > 0])
    antennas = dict (
      inp = ("push", types),
    )
    outputs = {}
    for tnr, t in enumerate(types):
      outputs["outp%d" % (tnr+1)] = ("push", t)
    params = {
    }
    class unweaver(object):
      guiparams = dict (
        __beename__ = "unweaver",
        antennas = antennas,
        outputs = outputs,
        parameters = params,
      )
    return unweaver
