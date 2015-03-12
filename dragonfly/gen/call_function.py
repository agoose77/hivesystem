import bee
from bee.segments import *

import sys
import functools

python3 = (sys.version_info[0] == 3)


"""
Executes a string using python's exec function
Supports Output information with a shorthand Output function, or by accessing the worker directly
"""

class call_function(bee.worker):
    func = antenna("pull", ("object", "callable"))
    func_buffer = buffer("pull", ("object", "callable"))
    connect(func, func_buffer)

    result = output("pull", "object")
    output_variable = variable("object")
    connect(output_variable, result)

    args = antenna("pull", "object")
    args_buffer = buffer("pull", "object")
    connect(args, args_buffer)

    trig = antenna("push", "trigger")

    def parse_args(self):
        return [bee.resolve(a, self.parent) for a in self.args_buffer]

    @modifier
    def call(self):
        args = self.parse_args()
        self.output_variable = self.func_buffer(*args)

    def set_parent(self, parent):
        self.parent = parent

    trigger(trig, func_buffer)
    trigger(func_buffer, args_buffer)
    trigger(args_buffer, call)