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
        f.sensormode.options = "normal", "radar", "ray"
        f.sensormode.default = "normal"
        f.sensormode.optiontitles = "Normal", "Radar", "Ray"

        f.idmode.name = "ID mode"
        f.idmode.advanced = True
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound"
        f.idmode.default = "bound"
        f.idmode.optiontitles = "Unbound", "Bound"

    def __new__(cls, sensormode, idmode):
        assert sensormode in ("normal", "radar", "ray"), sensormode
        assert idmode in ("bound", "unbound"), idmode

        class near(bee.worker):
            __doc__ = cls.__doc__

            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))

            # Are we monitoring enter or leave events?
            eventmode = variable("str")
            parameter(eventmode)

            #How are the nearby objects filtered?
            filtermode = variable("str")
            parameter(filtermode)

            #What is the value of the filter?
            filtervalue = antenna("pull", "str")

            if sensormode in ("radar", "ray"):
                #What is the direction axis of the sensor
                axis = antenna("pull", "Coordinate")

            if sensormode == "radar":
                #Projection cone angle (in degrees)
                angle = antenna("pull", "float")

            #What distance causes a near event (enter/leave)?
            distance = antenna("pull", "float")

            #Has a near event (enter/leave) happened during the last tick?
            is_active = variable("bool")
            startvalue(is_active, False)
            active = output("pull", "bool")
            connect(is_active, active)

            #What was the ID of the near object?
            v_near_id = variable(("str", "identifier"))
            near_id = output("pull", ("str", "identifier"))
            connect(v_near_id, near_id)

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
                "angle": {"name": "Cone angle", "tooltip": "Projection cone angle (degrees)", "fold": True},
                "distance": {"name": "Distance", "fold": True},
                "active": {"name": "Active"},
                "near_id": {"name": "Near ID", "advanced": True},
                "_memberorder": ["filtervalue", "identifier", "axis", "angle", "distance", "near_id", "active"],
            }

            def place(self):
                raise NotImplementedError("sparta.sensors.near has not been implemented yet")

        return near
    