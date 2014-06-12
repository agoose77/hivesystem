import libcontext, bee
from bee.segments import *


class delay(object):
    """
    The delay trigger receives a signal and forwards it after a delay
    In single mode, receiving a new signal during the delay period resets it
    In multi mode, each signal is treated independently
    """
    metaguiparams = {
        "mode": "str",
        "autocreate": {"mode": "frames"},
    }

    @classmethod
    def form(cls, f):
        f.mode.name = "Mode"
        f.mode.type = "option"
        f.mode.options = "frames", "seconds"
        f.mode.optiontitles = "Delay in frames", "Delay in seconds"
        f.mode.default = "frames"

    def __new__(cls, mode):
        class delay(bee.worker):
            __doc__ = cls.__doc__

            trig = output("push", "trigger")
            trigfunc = triggerfunc(trig)

            if mode == "frames":
                delay = antenna("pull", "int")
                b_delay = buffer("pull", "int")
            elif mode == "seconds":
                delay = antenna("pull", "float")
                b_delay = buffer("pull", "float")
            connect(delay, b_delay)

            multi = variable("bool")
            parameter(multi, False)

            # Name the inputs and outputs
            guiparams = {
                "delay": {"name": "delay", "fold": True},
                "trig": {"name": "Trigger"},
            }

            @staticmethod
            def form(f):
                f.multi.name = "Multi mode"
                f.multi.advanced = True

            def place(self):
                raise NotImplementedError("sparta.triggers.delay has not been implemented yet")

        return delay