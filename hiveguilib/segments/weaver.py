"""
Dummy node for bee.segments.weaver in the GUI
"""
class weaver(object):
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
    antennas = {}
    for tnr, t in enumerate(types):
      antennas["inp%d" % (tnr+1)] = ("pull", t)
    outputs = dict (
      outp = ("pull", types),
    )
    params = {
    }
    class weaver(object):
      guiparams = dict (
        __beename__ = "weaver",
        antennas = antennas,
        outputs = outputs,
        parameters = params,
      )
    return weaver
