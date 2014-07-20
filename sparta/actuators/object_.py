import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from dragonfly import std, convert

from .launch import launch_helper, id_suffix_worker


class object_helper(bee.worker):

    class_ = antenna("pull", ("str", "identifier"))
    b_class = buffer("pull", ("str", "identifier"))
    connect(class_, b_class)

    identifier_ = antenna("pull", ("str", "identifier"))
    b_identifier = buffer("pull", ("str", "identifier"))
    connect(identifier_, b_identifier)

    placement = antenna("pull", ("object", "matrix"))
    b_placement = buffer("pull", ("object", "matrix"))
    connect(placement, b_placement)

    output_entity = output("pull", ("str", "identifier"))
    v_output_entity = variable(("str", "identifier"))
    connect(v_output_entity, output_entity)

    output_process_class = output("pull", ("str", "identifier"))
    v_output_process_class = variable(("str", "identifier"))
    connect(v_output_process_class, output_process_class)

    # For launch worker
    trig_out = output("push", "trigger")
    do_trigger = triggerfunc(trig_out)

    # To start spawn
    trig = antenna("push", "trigger")

    trigger(trig, b_class)
    trigger(trig, b_identifier)
    trigger(trig, b_placement)

    @modifier
    def do_spawn(self):
        entity_class = self.b_class
        entity_name = self.b_identifier
        placement = self.b_placement

        self.spawn_entity(entity_class, entity_name)
        matrix = self.get_matrix(entity_name)

        # Set placement
        matrix.origin = placement.origin
        matrix.x = placement.x
        matrix.y = placement.y
        matrix.z = placement.z
        matrix.commit()

        hive_map_name = self.get_hivemap(entity_class)
        if hive_map_name is None:
            return

        # if we have a hivemap, cascade trigger
        self.v_output_process_class = hive_map_name
        self.v_output_entity = entity_name
        self.do_trigger()

    trigger(trig, do_spawn)

    def set_spawn_entity(self, func):
        self.spawn_entity = func

    def set_get_hivemap(self, func):
        self.get_hivemap = func

    def set_get_matrix(self, func):
        self.get_matrix = func

    def place(self):
        libcontext.socket(("entity", "spawn"), socket_single_required(self.set_spawn_entity))
        libcontext.socket(("entity", "class", "hivemap"), socket_single_required(self.set_get_hivemap))
        libcontext.socket(("entity", "matrix", "AxisSystem"), socket_single_required(self.set_get_matrix))


class object_(object):
    """
    The object actuator creates a new 3D object of "object class" at "location".  
    If a process class of the same name as "object class" has been registered, launch it. 
    Output contains the name of the last spawned object.
    """

    metaguiparams = {
        "config": "Launch",
        "autocreate": {"config":{"bind_event": True, "bind_hivereg": True, "bind_io":  True,
                                             "bind_sys": True, "bind_scene": True, "bind_time": True,
                                             "bind_entity": True, "bind_matrix": "relative"}},
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
            spawn_helper = object_helper()
            hive_binder = worker()
            id_factory = id_suffix_worker()

            # To push identifier base in id factory
            id_transistor = std.transistor(("str", "identifier"))()
            bee.connect(id_transistor.outp, id_factory.identifier_base)

            # Create some hive IO pins
            trig = bee.antenna(id_transistor.trig)
            bee.connect(id_factory.trig_out, spawn_helper.trig)
            bee.connect(spawn_helper.trig_out, bind_worker.trig)
            bee.connect(spawn_helper.output_process_class, bind_worker.process_class)

            # Secondary calls
            entity_class = bee.antenna(id_transistor.inp)
            bee.connect(entity_class, spawn_helper.class_)

            # Secondary calls
            process_identifier = bee.output(id_factory.new_identifier)
            bee.connect(process_identifier, bind_worker.process_identifier)
            bee.connect(process_identifier, spawn_helper.identifier_)

            placement = bee.antenna(spawn_helper.placement)
            entity_identifier = bee.output(spawn_helper.output_entity)

            # Weaver of these two
            w_bind_ids = std.weaver(("id", "id"))()

            process_id_duck = convert.pull.duck("str", "id")()

            bee.connect(id_factory.new_identifier, process_id_duck)
            bee.connect(process_id_duck, w_bind_ids.inp1)

            process_class_duck = convert.pull.duck("str", "id")()

            bee.connect(spawn_helper.output_process_class, process_class_duck)
            bee.connect(process_class_duck, w_bind_ids.inp2)

            # Connect weaver to binder
            t_bind_ids = std.transistor(("id", "id"))()
            bee.connect(w_bind_ids, t_bind_ids)
            bee.connect(t_bind_ids, hive_binder.bind)

            # This only triggers if we're a subprocess
            bee.connect(bind_worker.trig_out, t_bind_ids.trig)

            guiparams = {
                "entity_class": {"name": "Entity class", "fold": True},
                "placement": {"name": "Placement", "fold": True},
                "trig": {"name": "Trigger"},
                "entity_identifier": {"name": "Entity Identifier"},
                "process_identifier": {"name": "Process Identifier"},
                "subprocess": {"name": "Subprocess"},
                "memberorder": ["trig", "entity_class", "placement", "process_identifier", "entity_identifier"],
            }

        return launch




