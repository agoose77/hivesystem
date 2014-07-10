import bee

from .bindworkerinterface import bindworkerinterface
from .hiveregister import hiveregister
from .. import std, event, convert


class pluginbinderhive(object):

    """Connect bindworkerinterface with a bind class worker.

    Used to drive binding from a binder drone
    """

    def __new__(cls, bind_class):

        class dynamicbindhive_(bee.frame):
            # Create a binder worker
            hive_binder = bind_class().worker()

            bind_worker = bindworkerinterface()

            # Weaver of these two
            w_bind_ids = std.weaver(("id", "id"))()
            bee.connect(bind_worker.process_identifier, w_bind_ids.inp1)
            bee.connect(bind_worker.hivemap_name, w_bind_ids.inp2)

            # Connect weaver to binder
            t_bind_ids = std.transistor(("id", "id"))()
            bee.connect(w_bind_ids, t_bind_ids)
            bee.connect(t_bind_ids, hive_binder.bind)

            bee.connect(bind_worker.trig, t_bind_ids.trig)

            # TODO more event types
            head = convert.pull.duck("id", "event")()
            bee.connect(bind_worker.process_identifier, head)

            keyboardevents = event.sensor_match_leader("keyboard")
            add_head = event.add_head()
            bee.connect(keyboardevents, add_head)

            bee.connect(head, add_head)
            bee.connect(add_head, hive_binder.event)

            hivereg = hiveregister()

        return dynamicbindhive_