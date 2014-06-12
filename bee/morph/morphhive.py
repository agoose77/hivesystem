import bee
from bee import connect
from bee.pin import mediator, pinconnect, disconnect, remove, create

import dragonfly.consolehive


class morphhive(dragonfly.consolehive.consolehive):
    # ## exception handling
    raiser = bee.raiser()
    connect("evexc", raiser)

    ### pin drones
    mediator()
    pinconnect = pinconnect()
    disconnect = disconnect()
    remove = remove()
    create = create()

