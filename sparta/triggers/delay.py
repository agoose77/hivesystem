import libcontext, bee
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
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

            trig = antenna("push", "trigger")

            trig_deferred = output("push", "trigger")
            trigfunc = triggerfunc(trig_deferred)

            if mode == "frames":
                delay = antenna("pull", "int")
                b_delay = buffer("pull", "int")

                @property
                def time_value(self):
                    return self.pacemaker.ticks

            elif mode == "seconds":
                delay = antenna("pull", "float")
                b_delay = buffer("pull", "float")

                @property
                def time_value(self):
                    return self.pacemaker.time

            connect(delay, b_delay)
            trigger(trig, b_delay)

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

            @modifier
            def add_callback(self):
                self.pending_triggers.append(self.time_value + self.b_delay)

            trigger(b_delay, add_callback)

            def update_triggers(self):
                """Check for any valid triggers and run them"""
                time_value = self.time_value
                pending_times = self.pending_triggers[:]

                for target_time in pending_times:
                    if target_time > time_value:
                        continue

                    self.pending_triggers.remove(target_time)
                    self.trigfunc()

            def set_add_listener(self, add_listener):
                self.add_listener = add_listener

            def set_pacemaker(self, pacemaker):
                self.pacemaker = pacemaker

            def enable(self):
                # Add a high-priority deactivate() listener on every tick
                self.add_listener("trigger", self.update_triggers, "tick", priority=9)

            def place(self):
                self.pending_triggers = []
                libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))

                libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
                libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))

        return delay