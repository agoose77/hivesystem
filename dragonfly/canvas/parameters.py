class parameters(object): 
  def __init__(self, **args):
    for a in args: setattr(self, a, args[a])
