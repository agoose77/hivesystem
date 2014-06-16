import bee
from bee.segments import *

import functools

"""
Executes a string using python's exec function
Supports output information with a shorthand output function, or by accessing the worker directly
"""

class call_function_input(bee.worker):
    arg = antenna("pull", "object")
    arg_buffer = buffer("pull", "object")
    connect(arg, arg_buffer)


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

    trigger(trig, arg_buffer)
    trigger(arg_buffer, func_buffer)
    trigger(func_buffer, args_buffer)
    trigger(args_buffer, call)