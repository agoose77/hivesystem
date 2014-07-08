import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class near(object):
    """
    The near sensor detects other objects that are nearby
    The other objects can be filtered by material, property or identifier
    """
    metaguiparams = {
        "sensormode": "str",
        "idmode": "str",
        "autocreate": {"sensormode": "normal", "idmode": "bound"},
    }

    @classmethod
    def form(cls, f):
        f.sensormode.name = "Sensor mode"
        f.sensormode.type = "option"
        f.sensormode.options = "normal", "ray"
        f.sensormode.default = "normal"
        f.sensormode.optiontitles = "Normal", "Ray"

        f.idmode.name = "ID mode"
        f.idmode.advanced = True
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound"
        f.idmode.default = "bound"
        f.idmode.optiontitles = "Unbound", "Bound"

    def __new__(cls, sensormode, idmode):
        assert sensormode in ("normal", "ray"), sensormode
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

            if sensormode == "ray":
                #What is the direction axis of the sensor
                axis = antenna("pull", "Coordinate")
                b_axis = buffer("pull", "Coordinate")
                connect(axis, b_axis)
                trigger(b_filtervalue, b_axis)

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
                result = self.contact_test(self.entity_name, node)
                found_results = bool(result.contacts)
                self.is_active = found_results
                # TODO Panda?
                self.v_near_id = result.contacts[0].node_b if found_results else ""


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
                "axis": {"name": "Axis", "tooltip": "Projection axis", "fold": True},
                "distance": {"name": "Distance", "fold": True},
                "active": {"name": "Active"},
                "near_id": {"name": "Near ID", "advanced": True},
                "_memberorder": ["filtervalue", "identifier", "axis", "distance", "near_id", "active"],
            }

            def set_create_sphere_node(self, func):
                self.create_sphere_node = func

            def set_contact_test(self, func):
                self.contact_test = func

            def place(self):
                if idmode == "bound":
                    libcontext.socket(("entity", "bound"), socket_single_required(self.set_get_entity_name))

                libcontext.socket(("collision", "create_node", "sphere"),
                                  socket_single_required(self.set_create_sphere_node))
                libcontext.socket(("collision", "contact_test"),
                                  socket_single_required(self.set_contact_test))

        return near