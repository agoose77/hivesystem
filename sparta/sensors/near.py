import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class near(object):

    """The near sensor detects other objects that are nearby
    The other objects can be filtered by material, property or identifier"""

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

        class near(bee.worker):
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

            else:
                def set_get_entity_name(self, get_entity_name):
                    self.get_entity_name = get_entity_name

                @property
                def entity_name(self):
                    return self.get_entity_name()

            # Are we monitoring enter or leave events?
            eventmode = variable("str")
            parameter(eventmode)

            #How are the nearby objects filtered?
            filtermode = variable("str")
            parameter(filtermode)

            #What is the value of the filter?
            filtervalue = antenna("pull", "str")
            b_filtervalue = buffer("pull", "str")
            connect(filtervalue, b_filtervalue)

            trigger_inputs = triggerfunc(b_filtervalue)

            #What distance causes a near event (enter/leave)?
            distance = antenna("pull", "float")
            b_distance = buffer("pull", "float")
            connect(distance, b_distance)
            trigger(b_filtervalue, b_distance)

            #Has a near event (enter/leave) happened during the last tick?
            is_active = variable("bool")
            startvalue(is_active, False)
            active = output("pull", "bool")
            connect(is_active, active)

            #What was the ID of the near object?
            v_near_id = variable(("str", "identifier"))
            near_id = output("pull", ("str", "identifier"))
            connect(v_near_id, near_id)

            @modifier
            def do_near(self):
                self.trigger_inputs()
                node = self.create_sphere_node(self.b_distance, True)

                # Get entity name of the caller
                entity_name = self.entity_name

                # Get start position
                source_position = self.get_matrix(entity_name).origin

                # Test for material / property / ID
                filter_func = self.get_filter_func()
                # Don't test for self
                name_filter = lambda name: name != entity_name

                callback = lambda value: name_filter(value) and filter_func(value)

                result = self.contact_test(source_position, node, filter_func=callback)
                found_results = bool(result.contacts)

                self.is_active = found_results

                # TODO Panda?
                if found_results:
                    self.v_near_id = result.contacts[0].node_b

            pretrigger(v_near_id, do_near)
            pretrigger(is_active, do_near)

            @staticmethod
            def form(f):
                f.eventmode.name = "Filter mode"
                f.eventmode.type = "option"
                f.eventmode.advanced = True
                f.eventmode.default = "enter"
                f.eventmode.options = "enter", "leave"
                f.eventmode.optiontitles = "Enter events", "Leave events"

                f.filtermode.name = "Filter mode"
                f.filtermode.type = "option"
                f.filtermode.default = "id"
                f.filtermode.options = "material", "property", "id"
                f.filtermode.optiontitles = "By material", "By property", "By ID"

            guiparams = {
                "identifier": {"name": "Identifier", "fold": True},
                "filtervalue": {"name": "Filter value", "fold": True},
                "distance": {"name": "Distance", "fold": True},
                "active": {"name": "Active"},
                "near_id": {"name": "Near ID", "advanced": True},
                "_memberorder": ["filtervalue", "identifier", "distance", "near_id", "active"],
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

            def set_create_sphere_node(self, func):
                self.create_sphere_node = func

            def set_contact_test(self, func):
                self.contact_test = func

            def set_get_matrix(self, func):
                self.get_matrix = func

            def set_get_property(self, get_property):
                self.get_property = get_property

            def set_get_material(self, get_material):
                self.get_material = get_material

            def place(self):
                if idmode == "bound":
                    libcontext.socket(("entity", "bound"), socket_single_required(self.set_get_entity_name))

                libcontext.socket(("entity", "matrix", "AxisSystem"), socket_single_required(self.set_get_matrix))
                libcontext.socket(("collision", "create_node", "sphere"),
                                  socket_single_required(self.set_create_sphere_node))
                libcontext.socket(("collision", "contact_test"), socket_single_required(self.set_contact_test))
                libcontext.socket(("entity", "property", "get"), socket_single_required(self.set_get_property))
                libcontext.socket(("entity", "material", "get"), socket_single_required(self.set_get_property))

        return near