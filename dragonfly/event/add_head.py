import bee
from bee.segments import *


def op_add_head(event, head):
    return event.add_head(head)


class add_head(bee.worker):
    event = antenna("push", "event")
    v_event = variable("event")
    connect(event, v_event)

    head = antenna("pull", "event")

    w = weaver(("event", "event"), v_event, head)
    t = transistor(("event", "event"))
    connect(w, t)

    op = operator(op_add_head, ("event", "event"), "event")
    connect(t, op)

    outp = output("push", "event")
    connect(op, outp)

    trigger(v_event, t)
  
  
