import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from bee.spyderhive.hivemaphive import hivemapinithive
from dragonfly import std, convert

from ..models import Launch


def id_generator():
    """Yield unique integer id"""
    i = 0
    while True:
        yield i
        i += 1


class launch(object):

    """The launch actuator launches a new hive process.

    If subprocess is enabled, the launched hive uses the configuration options and launches a child process"""

    metaguiparams = {
        "config": "Launch",
        "subprocess": "bool",
        "autocreate": {"subprocess": True, "config": "Launch (\n  bind_event = True,\n  bind_hivereg = True,\n  bind_io = True,\n  bind_sys = True,\n  bind_scene = True,\n  bind_time = True\n)"},
        "_memberorder": ["config", "subprocess"]
    }

    @classmethod
    def form(cls, f):
        f.config.name = "Launch Options"
        f.config.advanced = True

    def __new__(cls, config, subprocess):
        # This is annoying
        if isinstance(config, str):
            import Spyder
            config = Spyder.Launch(config)

        worker = config.make_launch()

        class launch_(bee.worker):

            """Interfaces with BindWorker from configuration options"""

            _id_generator = id_generator()

            process_class = antenna("pull", ("str", "identifier"))
            b_process_class = buffer("pull", ("str", "identifier"))
            connect(process_class, b_process_class)

            process_identifier = output("pull", ("str", "process"))
            v_process_id = variable(("str", "process"))
            connect(v_process_id, process_identifier)

            trig_out = output("push", "trigger")
            do_trig = triggerfunc(trig_out)

            trig = antenna("push", "trigger")

            @modifier
            def setup_launch(self):
                hivemap_name = self.b_process_class
                identifier = self.get_unique_process_id(hivemap_name)

                self.v_process_id = identifier

                # Delegate to main bindworker
                if not subprocess:
                    self.launch_process(hivemap_name, identifier)
                    return

                # Delegate to bindworker
                # Check if it is registered
                try:
                    self.get_func(hivemap_name)

                # Else register it so the dragonfly.bind mixin can access it
                except KeyError:
                    hivemap_ = Spyder.Hivemap.fromfile(hivemap_name)
                    wrapper_hive = type(hivemap_name, (hivemapinithive,), dict(hivemap=hivemap_))
                    self.register_func(hivemap_name, wrapper_hive)

                self.do_trig()

            trigger(trig, b_process_class)
            trigger(trig, setup_launch)

            def get_unique_process_id(self, process_class_identifier):
                """Create a unique id for the current process.

                Ensure that any users of the launch actuator don't share identifiers.

                :param process_class_identifier: id of process class
                """
                return "{}_{}".format(process_class_identifier, next(self._id_generator))

            # Mark "object class" as an initially folded, and define the I/O names
            guiparams = {
                "trig": {"name": "Trigger"},
                "process_class": {"name": "Process class", "fold": True},
                "process": {"name": "Process"},
                "_memberorder": ["trig", "process_class", "process"],
            }

            def set_launch_process(self, launch_process):
                self.launch_process = launch_process

            @classmethod
            def form(cls, f):
                f.subprocess.name = "Subprocess"
                f.subprocess.advanced = True

            def set_register_hive(self, register_func):
                self.register_func = register_func

            def set_get_hive(self, get_func):
                self.get_func = get_func

            def place(self):
                # If we are launching a subprocess, use the main hive launch plugin
                if not subprocess:
                    socket = socket_single_required(self.set_launch_process)
                    libcontext.socket(("process", "launch"), socket)

                # Otherwise we must register the hivemap for the bindworker
                else:
                    socket = socket_single_required(self.set_register_hive)
                    libcontext.socket("register_hive", socket)

                    socket = socket_single_required(self.set_get_hive)
                    libcontext.socket("get_hive", socket)


        class launch_hive(bee.frame):
            __doc__ = cls.__doc__

            bind_worker = launch_()
            hive_binder = worker()

            # Create some hive IO pins
            trig = bee.antenna(bind_worker.trig)
            process_class = bee.antenna(bind_worker.process_class)
            process_identifier = bee.output(bind_worker.process_identifier)

            # Weaver of these two
            w_bind_ids = std.weaver(("id", "id"))()

            process_id_duck = convert.pull.duck("str", "id")()

            bee.connect(process_identifier, process_id_duck)
            bee.connect(process_id_duck, w_bind_ids.inp1)

            process_class_duck = convert.pull.duck("str", "id")()

            bee.connect(process_class, process_class_duck)
            bee.connect(process_class_duck, w_bind_ids.inp2)

            # Connect weaver to binder
            t_bind_ids = std.transistor(("id", "id"))()
            bee.connect(w_bind_ids, t_bind_ids)
            bee.connect(t_bind_ids, hive_binder.bind)

            # This only triggers if we're a subprocess
            bee.connect(bind_worker.trig_out, t_bind_ids.trig)


        return launch_hive