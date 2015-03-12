import bee
from bee.segments import *
import functools

"""
Executes a string using python's exec function
Supports Output information with a shorthand Output() function, or by accessing the worker directly
"""


class execute(bee.worker):
    command = antenna("pull", "str")
    command_buffer = buffer("pull", "str")
    connect(command, command_buffer)

    result = output("pull", "object")
    result_variable = variable("object")
    connect(result_variable, result)

    @modifier
    def call(self):
        def output(obj):
            self.result_variable = obj

        try:
            exec(self.command_buffer)
        except Exception as err:
            raise err

    pretrigger(result_variable, command_buffer)
    trigger(command_buffer, call)

    def set_parent(self, parent):
        self.parent = parent
