import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class collision(object):
    """
    The collision sensor reports collisions between a specific object and all other objects
    The other objects can be filtered by material, property or identifier
    """
    metaguiparams = {
        "idmode": "str",
        "autocreate": {"idmode": "bound"},
    }

    @classmethod
    def form(cls, f):
        f.idmode.name = "ID mode"
        f.idmode.advanced = True
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound"
        f.idmode.default = "bound"
        f.idmode.optiontitles = "Unbound", "Bound"

    def __new__(cls, idmode):
        assert idmode in ("bound", "unbound"), idmode

        class collision(bee.worker):
            __doc__ = cls.__doc__

            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))
                identifier_buffer = buffer("pull", ("str", "identifier"))
                connect(identifier, identifier_buffer)
                trigger_identifier_buffer = triggerfunc(identifier_buffer)

                @property
                def entity_name(self):
                    self.trigger_identifier_buffer()
                    return self.identifier_buffer

            # How are the collisions filtered?
            filter_mode = variable("str")
            parameter(filter_mode)

            #What is the value of the filter?
            filter_value = antenna("pull", "str")
            filter_buffer = buffer("pull", "str")
            connect(filter_value, filter_buffer)

            #Has a collision event happened during the last tick?
            is_active = variable("bool")
            startvalue(is_active, False)
            active = output("pull", "bool")
            connect(is_active, active)

            #What was the ID of the colliding object?
            collision_id_variable = variable(("str", "identifier"))
            collision_id = output("pull", ("str", "identifier"))
            connect(collision_id_variable, collision_id)

            trigger_filter_value = triggerfunc(filter_buffer)

            @staticmethod
            def form(f):
                f.filter_mode.name = "Filter mode"
                f.filter_mode.type = "option"
                f.filter_mode.default = "id"
                f.filter_mode.options = "material", "property", "id"
                f.filter_mode.optiontitles = "By material", "By property", "By ID"

            guiparams = {
                "identifier": {"name": "Identifier", "fold": True},
                "filter_value": {"name": "Filter value", "fold": True},
                "active": {"name": "Active"},
                "collision_id": {"name": "Collision ID", "advanced": True},
                "_memberorder": ["filter_value", "identifier", "collision_id", "active"],
                }

            if idmode == "unbound":
                def get_collisions(self):
                    return self.get_collisions_for(self.entity_name)

            def update_value(self):
                filter_func = self.get_filter_func()

                # Request filter value
                self.trigger_filter_value()
                filter_value = self.filter_buffer

                # Find a valid collision
                for collision_identifier in self.get_collisions():
                    if filter_func(collision_identifier, filter_value):
                        break
                else:
                    collision_identifier = None

                # Set outputs
                self.collision_id_variable = collision_identifier
                self.is_active = collision_identifier is not None

            def get_filter_func(self):
                """Find an appropriate filter function"""
                filter_mode = self.filter_mode
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

            def enable(self):
                self.add_listener("trigger", self.update_value, "tick", priority=9)

            def set_get_collisions(self, get_collisions):
                self.get_collisions = get_collisions

            def set_get_collisions_for(self, get_collisions_for):
                self.get_collisions_for = get_collisions_for

            def set_get_property(self, get_property):
                self.get_property = get_property

            def set_get_entity(self, get_entity):
                self.get_entity = get_entity

            def set_get_material(self, get_material):
                self.get_material = get_material

            def place(self):
                if idmode == "bound":
                    libcontext.socket(("entity", "bound", "collisions"), socket_single_required(self.set_get_collisions))

                libcontext.socket(("entity", "collisions"), socket_single_required(self.set_get_collisions_for))
                libcontext.socket(("entity", "property", "get"), socket_single_required(self.set_get_property))
                libcontext.socket(("entity", "material", "get"), socket_single_required(self.set_get_property))

        return collision
