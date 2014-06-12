import bee
from bee.segments import *
import functools

"""
Calls a function with input argument and optional pre-set arguments 
Supports the bee.resolve interface 
"""
import sys

python3 = (sys.version_info[0] == 3)


class call0(bee.worker):
    inp = antenna("push", "trigger")
    func = variable(("object", "callable"))
    parameter(func)
    args = variable("object")
    parameter(args, tuple())

    @modifier
    def call(self):
        if isinstance(self.args, tuple):
            args = self.args
        else:
            args = (self.args,)
        args = [bee.resolve(a, self.parent) for a in args]
        if isinstance(self.func, functools.partial):
            self.func(*args)
        elif python3:
            self.func.__func__(*args)
        else:
            self.func.im_func(*args)

    trigger(inp, call)

    def set_parent(self, parent):
        self.parent = parent
  
