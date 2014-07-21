import libcontext
from bee.bind import *
import bee.event

from ..event.bind import eventlistener


class bind(bind_baseclass):
    bind_pacemaker = bindparameter("transmit")
    # TODO check if this can be disabled
    binder("bind_pacemaker", "transmit", pluginbridge("pacemaker"))
    binder("bind_pacemaker", False, None)
    # TODO: binder("bind_pacemaker", "simple")

    transmit_tick = bindparameter("evin")
    binder("transmit_tick", False, None)
    binder("transmit_tick", "evin", eventlistener("tick"), "bindname")
    #TODO: binder("transmit_tick", "pacemaker", tickforwarder_pacemaker(), "bindname") TODO in case of separate pacemaker


# NOTE: pacemaker must generate a start event on first use

#note the difference between:
# 1. having the same pacemaker+tick pause (time workers get not updated, but catch up)
# 2. having different pacemakers+tick pause (tick time workers do not catch up; time workers do, unless you control the pacemaker's
#  time as well, TODO)
