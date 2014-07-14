import libcontext
from . import worker, drone


class bindbridge(drone):
    def __init__(self, bindobject):
        self.bindobject = bindobject

    def place(self):
        for binder in self.bindobject.binder_instances:
            if getattr(self.bindobject, binder.parameter_name) != binder.parameter_value:
                continue
            # print binder.parameter_name, binder.parametervalue, str(binder.binder_drone_instance.__beename__), tuple(binder.antennanames)
            if len(binder.antenna_names):
                if binder.antenna_names != ["bindname"]:
                    raise TypeError("Static binder worker cannot provide bindantennas %s" % list(binder.antenna_names))
                binder.binder_drone_instance.bind(self.bindobject, bindname=self.bindobject.b_bindname)
            else:
                binder.binder_drone_instance.bind(self.bindobject)
        s = libcontext.socketclasses.socket_supplier(lambda f: self.bindobject.startupfunctions.append(f))
        libcontext.socket("startupfunction", s)

