import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from bee.spyderhive.hivemaphive import hivemapinithive
from dragonfly import std, convert

from .launch import id_generator


class object_(object):
    """
    The object actuator creates a new 3D object of "object class" at "location".  
    If a process class of the same name as "object class" has been registered, launch it. 
    Output contains the name of the last spawned object.
    """
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

            # Entity type
            class_ = antenna("pull", ("str", "identifier"))
            b_class = buffer("pull", ("str", "identifier"))
            connect(class_, b_class)

            # Transform matrix
            placement = antenna("pull", ("object", "matrix"))
            b_placement = buffer("pull", ("object", "matrix"))
            connect(placement, b_placement)

            # Output entity
            output_entity = output("pull", ("str", "identifier"))
            v_output_entity = variable(("str", "identifier"))
            connect(v_output_entity, output_entity)

            # Output process
            process_identifier = output("pull", ("str", "process"))
            v_process_id = variable(("str", "process"))
            connect(v_process_id, process_identifier)

            # Carry trigger
            trig_out = output("push", "trigger")
            do_trig = triggerfunc(trig_out)

            # Launch trigger
            trig = antenna("push", "trigger")

            trigger(trig, b_class)
            trigger(trig, b_placement)

            @modifier
            def setup_launch(self):
                class_name = self.b_class
                identifier = self.get_unique_process_id(class_name)

                self.spawn_entity(class_name, identifier)

                try:
                    hivemap_name = self.get_class_hivemap(class_name)

                except KeyError:
                    pass

                else:
                    self.launch_process(hivemap_name, identifier)

            def launch_process(self, hivemap_name, identifier):
                """Launch hivemap process for entity"""

                self.v_process_id = identifier

                # Delegate to bindworker
                # Check if it is registered
                try:
                    self.get_func(hivemap_name)

                # Else register it so the dragonfly.bind mixin can access it
                except KeyError:
                    try:
                        hivemap_ = Spyder.Hivemap.fromfile(hivemap_name)

                    except Exception:
                        print("Couldn't find hivemap {} to launch".format(hivemap_name))
                        return

                    wrapper_hive = type(hivemap_name, (hivemapinithive,), dict(hivemap=hivemap_))
                    self.register_func(hivemap_name, wrapper_hive)

                # TODO asset management -> register factory for producing object
                # TODO use entityclassloader and get rid of scene loader drone

                # Delegate to main bindworker
                if not subprocess:
                    self.launch_main_process(hivemap_name, identifier)

                else:
                    self.do_trig()

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

            def set_launch_main_process(self, launch_main_process):
                self.launch_main_process = launch_main_process

            @classmethod
            def form(cls, f):
                f.subprocess.name = "Subprocess"
                f.subprocess.advanced = True

            def set_register_hive(self, register_func):
                self.register_func = register_func

            def set_get_hive(self, get_func):
                self.get_func = get_func

            def set_get_hivemap(self, get_hivemap):
                self.get_class_hivemap = get_hivemap

            def set_spawn_entity(self, entity_spawn):
                self.spawn_entity = entity_spawn

            def place(self):
                # If we are launching a subprocess, use the main hive launch plugin
                if not subprocess:
                    socket = socket_single_required(self.set_launch_main_process)
                    libcontext.socket(("process", "launch"), socket)

                # Otherwise we must register the hivemap for the bindworker
                else:
                    socket = socket_single_required(self.set_register_hive)
                    libcontext.socket("register_hive", socket)

                    socket = socket_single_required(self.set_get_hive)
                    libcontext.socket("get_hive", socket)

                socket = socket_single_required(self.set_get_hivemap)
                libcontext.socket(("entity", "class", "hivemap"), socket)

                socket = socket_single_required(self.set_spawn_entity)
                libcontext.socket(("entity", "spawn"), socket)


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

    def __new__(cls):
        # Inputs and outputs
        trig = antenna("push", "trigger")

        class_ = antenna("pull", ("str", "identifier"))
        b_class = buffer("pull", ("str", "identifier"))
        connect(class_, b_class)

        placement = antenna("pull", ("object", "matrix"))
        b_placement = buffer("pull", ("object", "matrix"))
        connect(placement, b_placement)

        output_entity = output("pull", ("str", "identifier"))
        v_output_entity = variable(("str", "identifier"))
        connect(v_output_entity, output_entity)

        output_process = output("pull", ("str", "identifier"))
        v_output_process = variable(("str", "identifier"))
        connect(v_output_process, output_process)

        subprocess = variable("bool")
        parameter(subprocess, True)

        @modifier
        def do_spawn(self):
            pass

        trigger(trig, do_spawn)


        # Mark "object class" as an initially folded, and define the I/O names
        guiparams = {
            "trig": {"name": "Trigger"},
            "class_": {"name": "Object Class", "fold": True},
            "placement": {"name": "Object Placement"},
            "output_entity": {"name": "Output"},
            "output_process": {"name": "Output"},
            "_memberorder": ["trig", "class_", "placement", "output_process", "output_entity"],
        }

        # Method to manipulate the parameter form as it appears in the GUI
        @staticmethod
        def form(f):
            f.subprocess.name = "Subprocess mode"
            f.subprocess.advanced = True

        # Finally, declare our sockets and plugins, to communicate with the rest of the hive
        def place(self):
            raise NotImplementedError("sparta.sensors.object_ has not been implemented yet")


     