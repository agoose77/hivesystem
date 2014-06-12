t = "any"

class push_antenna(object):
  guiparams = dict (
    __beename__ = "push_antenna",
    antennas = {},
    outputs = {"outp":("push",t)},
    parameters = {},
  )

class pull_antenna(object):
  guiparams = dict (
    __beename__ = "pull_antenna",
    antennas = {},
    outputs = {"outp":("pull",t)},
    parameters = {},
  )

class push_output(object):
  guiparams = dict (
    __beename__ = "push_output",
    antennas = {"inp":("push",t)},
    outputs = {},
    parameters = {},
  )

class pull_output(object):
  guiparams = dict (
    __beename__ = "pull_output",
    antennas = {"inp":("pull",t)},
    outputs = {},
    parameters = {},
  )
  
