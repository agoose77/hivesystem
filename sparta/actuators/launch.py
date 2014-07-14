import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from bee.spyderhive.hivemaphive import hivemapinithive
from dragonfly import std, convert

from ..models import Launch
import Spyder


def id_generator():
    """Yield unique integer id"""
    i = 0
    while True:
        yield i
        i += 1


class launch_helper(bee.worker):

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

    subprocess = variable("bool")
    parameter(subprocess)

    @modifier
    def setup_launch(self):
        hivemap_name = self.b_process_class
        identifier = self.get_unique_process_id(hivemap_name)

        self.v_process_id = identifier

        # Delegate to bindworker
        # Check if it is registered
        try:
            self.get_hive(hivemap_name)

        # Else register it so the dragonfly.bind mixin can access it
        except KeyError:
            try:
                hivemap_ = Spyder.Hivemap.fromfile(hivemap_name)

            except Exception:
                print("Couldn't find hivemap {} to launch".format(hivemap_name))
                return

            wrapper_hive = type(hivemap_name, (hivemapinithive,), dict(hivemap=hivemap_))
            self.register_hive(hivemap_name, wrapper_hive)

        # Delegate to main bindworker
        if not self.subprocess:
            self.launch_process(hivemap_name, identifier)

        else:
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

    def set_launch_process(self, launch_process):
        self.launch_process = launch_process

    def set_register_hive(self, register_hive):
        self.register_hive = register_hive

    def set_get_hive(self, get_hive):
        self.get_hive = get_hive

    def place(self):
        # If we are launching a subprocess, use the main hive launch plugin
        if not self.subprocess:
            socket = socket_single_required(self.set_launch_process)
            libcontext.socket(("process", "launch"), socket)

        socket = socket_single_required(self.set_register_hive)
        libcontext.socket("register_hive", socket)

        socket = socket_single_required(self.set_get_hive)
        libcontext.socket("get_hive", socket)


class launch(object):

    """The launch actuator launches a new hive process.

    If subprocess is enabled, the launched hive uses the configuration options and launches a child process"""

    metaguiparams = {
        "config": "Launch",
        "autocreate": {"config": "Launch (\n  bind_event = True,\n  bind_hivereg = True,\n  bind_io = True,\n  bind_sys = True,\n  bind_scene = True,\n  bind_time = True\n)"},
        "_memberorder": ["config"]
    }

    @classmethod
    def form(cls, f):
        f.config.name = "Launch Options"
        f.config.advanced = True

    def __new__(cls, config):
        # Create custom bindworker
        if isinstance(config, str):
            import Spyder
            config = Spyder.Launch(config)

        worker = config.make_launch()

        class launch(bee.frame):
            __doc__ = cls.__doc__

            subprocess = bee.parameter("bool")

            bind_worker = launch_helper(subprocess=bee.get_parameter("subprocess"))
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

            guiparams = {
                "process_class": {"name": "Process class", "fold": True},
                "trig": {"name": "Trigger"},
                "process_identifier": {"name": "Process Identifier"},
            }


        return launch