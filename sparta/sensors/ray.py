import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class ray(object):

    """The ray sensor detects other objects that intersect with a line
    The other objects can be filtered by material, property or identifier"""

    metaguiparams = {
        "idmode": "str",
        "use_entity_position": "bool",
        "autocreate": {"idmode": "bound", "use_entity_position": True},
    }

    @classmethod
    def form(cls, f):
        f.idmode.name = "ID mode"
        f.idmode.advanced = True
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound"
        f.idmode.default = "bound"
        f.idmode.optiontitles = "Unbound", "Bound"

        f.use_entity_position.name = "From entity"

    def __new__(cls, idmode, use_entity_position):
        assert idmode in ("bound", "unbound"), idmode

        class ray(bee.worker):
            __doc__ = cls.__doc__

            if use_entity_position:
                if idmode == "unbound":
                    identifier = antenna("pull", ("str", "identifier"))
                    identifier_buffer = buffer("pull", ("str", "identifier"))
                    connect(identifier, identifier_buffer)
                    trigger_identifier_buffer = triggerfunc(identifier_buffer)

                    @property
                    def entity_name(self):
                        self.trigger_identifier_buffer()
                        return self.identifier_buffer

                else:
                    def set_get_entity_name(self, get_entity_name):
                        self.get_entity_name = get_entity_name

                    @property
                    def entity_name(self):
                        return self.get_entity_name()

            #How are the nearby objects filtered?
            filtermode = variable("str")
            parameter(filtermode)

            #What is the value of the filter?
            filtervalue = antenna("pull", "str")
            b_filtervalue = buffer("pull", "str")
            connect(filtervalue, b_filtervalue)

            if not use_entity_position:
                #What is the start position of the sensor
                start_position = antenna("pull", "Coordinate")
                b_start = buffer("pull", "Coordinate")
                connect(start_position, b_start)
                trigger(b_filtervalue, b_start)

            #What is the direction axis of the sensor
            axis = antenna("pull", "Coordinate")
            b_axis = buffer("pull", "Coordinate")
            connect(axis, b_axis)
            trigger(b_filtervalue, b_axis)

            #What distance does the ray travel?
            distance = antenna("pull", "float")
            b_distance = buffer("pull", "float")
            connect(distance, b_distance)
            trigger(b_filtervalue, b_distance)

            #Has a ray event happened during the last tick?
            is_active = variable("bool")
            startvalue(is_active, False)
            active = output("pull", "bool")
            connect(is_active, active)

            #What was the ID of the near object?
            v_hit_id = variable(("str", "identifier"))
            near_id = output("pull", ("str", "identifier"))
            connect(v_hit_id, near_id)

            #What is the hit position
            v_hit_pos = variable("Coordinate")
            hit_pos = output("pull", "Coordinate")
            connect(v_hit_pos, hit_pos)

            #What is the hit normal
            v_hit_normal = variable("Coordinate")
            hit_normal = output("pull", "Coordinate")
            connect(v_hit_normal, hit_normal)

            trigger_inputs = triggerfunc(b_filtervalue)

            @staticmethod
            def form(f):
                f.filtermode.name = "Filter mode"
                f.filtermode.type = "option"
                f.filtermode.default = "id"
                f.filtermode.options = "material", "property", "id"
                f.filtermode.optiontitles = "By material", "By property", "By ID"

            if not use_entity_position:
                @modifier
                def do_raycast(self):
                    self.trigger_inputs()

                    start = self.b_start
                    axis = self.b_axis
                    distance = self.b_distance

                    # Test for material / property / ID
                    filter_func = self.get_filter_func()

                    result = self.ray_test(start, axis, distance, filter_func=filter_func)

                    self.is_active = result is not None

                    if self.is_active:
                        self.v_hit_pos = result.hit_position
                        self.v_hit_normal = result.hit_normal
                        self.v_hit_id = result.hit_node

            else:
                @modifier
                def do_raycast(self):
                    self.trigger_inputs()

                    # Get entity name of the caller
                    entity_name = self.entity_name

                    # Get start position
                    start = self.get_matrix(entity_name).origin
                    axis = self.b_axis
                    distance = self.b_distance

                    # Test for material / property / ID
                    filter_func = self.get_filter_func()

                    # Don't test for self
                    name_filter = lambda name: name != entity_name

                    # Combine filters
                    callback = lambda value: name_filter(value) and filter_func(value)
                    result = self.ray_test(start, axis, distance, filter_func=callback)

                    self.is_active = result is not None

                    if self.is_active:
                        self.v_hit_pos = result.hit_position
                        self.v_hit_normal = result.hit_normal
                        self.v_hit_id = result.hit_node

            pretrigger(v_hit_id, do_raycast)
            pretrigger(is_active, do_raycast)


            guiparams = {
                "identifier": {"name": "Identifier", "fold": True},
                "start_position": {"name": "Start Position"},
                "filtervalue": {"name": "Filter value", "fold": True},
                "axis": {"name": "Axis", "tooltip": "Projection axis", "fold": True},
                "distance": {"name": "Distance", "fold": True},
                "active": {"name": "Active"},
                "near_id": {"name": "Hit Entity ID", "advanced": True},
                "hit_pos": {"name": "Hit Position", "advanced": True},
                "hit_normal": {"name": "Hit Normal", "advanced": True},
                "_memberorder": ["filtervalue", "start_position", "identifier", "axis", "distance", "near_id", "active",
                                 "hit_normal", "hit_pos"],
            }

            def get_filter_func(self):
                """Find an appropriate filter function"""
                filter_mode = self.filtermode
                if filter_mode == "material":
                    return self.match_material

                if filter_mode == "property":
                    return self.match_property

                if filter_mode == "id":
                    return self.match_identifier

            def match_material(self, entity_name, filter_value):
                """Determine if the entity has a matching material

                :param entity_name: name of filtered entity
                :param filter_value: required material name
                """

                try:
                    self.get_material(entity_name, filter_value)

                except KeyError:
                    return False

                return True

            @staticmethod
            def match_identifier(entity_name, filter_value):
                """Determine if the entity identifier matches the filter identifier

                :param entity_name: name of filtered entity
                :param filter_value: required entity identifier
                """
                return entity_name == filter_value

            def match_property(self, entity_name, filter_value):
                """Determine if the entity has a matching property

                :param entity_name: name of filtered entity
                :param filter_value: required property name
                """
                try:
                    self.get_property(entity_name, filter_value)

                except KeyError:
                    return False

                return True

            def set_ray_test(self, func):
                self.ray_test = func

            def set_get_property(self, get_property):
                self.get_property = get_property

            def set_get_material(self, get_material):
                self.get_material = get_material

            def place(self):
                if idmode == "bound" and use_entity_position:
                    libcontext.socket(("entity", "bound"), socket_single_required(self.set_get_entity_name))

                libcontext.socket(("collision", "ray_test"), socket_single_required(self.set_ray_test))
                libcontext.socket(("entity", "property", "get"), socket_single_required(self.set_get_property))
                libcontext.socket(("entity", "material", "get"), socket_single_required(self.set_get_property))

        return ray