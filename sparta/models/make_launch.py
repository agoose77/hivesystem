import bee.bind
import bee.staticbind
import dragonfly.event
import dragonfly.io
import dragonfly.sys
import dragonfly.scene
import dragonfly.time
import dragonfly.scene
import dragonfly.bind
from bee.staticbind import staticbind_baseclass
from bee.spyderhive.hivemaphive import hivemapinithive
import Spyder


def make_launch(config):
    print("WARNING: Launch.make_worker, INCOMPLETE implementation")
    baseclasses = []
    if config.bind_hivereg:
        baseclasses.append(dragonfly.bind.bind)
    if config.bind_io:
        baseclasses.append(dragonfly.io.bind)
    if config.bind_sys:
        baseclasses.append(dragonfly.sys.bind)
    if config.bind_scene:
        baseclasses.append(dragonfly.scene.bind)
    if config.bind_time:
        baseclasses.append(dragonfly.time.bind)
    if config.bind_event:
        baseclasses.append(dragonfly.event.bind)

    d = {}
    if config.bind_matrix is not None:
        k = config.bind_matrix
        v = True
        if k == "yes":
            v = True
        elif k == "no":
            v = False
        elif k == "relative":
            v = "relative"
        elif k == "camera":
            v = "camera"

        d["bind_matrix"] = v

    if config.bind_entity is not None:
        k = config.bind_entity
        v = True
        if k == "yes":
            v = True
        elif k == "no":
            v = False

        d["bind_entity"] = v

    if config.bind_stop is not None:
        k = config.bind_stop

        d["bind_stop"] = k

    if config.bind_keyboard is not None:
        k = config.bind_keyboard
        v = True
        if k == "no":
            v = False
        elif k == "direct":
            v = "direct"
        elif k == "indirect":
            v = "indirect"
        d["bind_keyboard"] = v

    if config.hivemap is not None:
        class bindhive(hivemapinithive):
            hivemap = Spyder.Hivemap.fromfile(config.hivemap)

        d["hive"] = bindhive

    bindworkerbind = type("bindworkerbind", tuple(baseclasses),d)
    return bindworkerbind.worker().__class__