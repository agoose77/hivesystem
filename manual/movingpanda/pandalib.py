import dragonfly
import dragonfly.pandahive
import bee
from bee import connect

import dragonfly.scene.unbound, dragonfly.scene.bound
import dragonfly.std
import dragonfly.io
import dragonfly.canvas
import dragonfly.convert.pull
import dragonfly.logic
import dragonfly.bind
import dragonfly.op.pull

import Spyder

# ## random matrix generator
from random import random


def random_matrix_generator():
    while 1:
        a = Spyder.AxisSystem()
        a.rotateZ(360 * random())
        a.origin = Spyder.Coordinate(15 * random() - 7.5, 15 * random() - 7.5, 0)
        yield dragonfly.scene.matrix(a, "AxisSystem")


def id_generator():
    n = 0
    while 1:
        n += 1
        yield "spawnedpanda" + str(n)


class myscene(dragonfly.pandahive.spyderframe):
    a = Spyder.AxisSystem()
    a *= 0.25
    a.origin += (-8, 42, 0)
    env = Spyder.Model3D("models/environment", "egg", a)

    camcenter = Spyder.Entity3D(
        "camcenter",
        (
            Spyder.NewMaterial("white", color=(255, 255, 255)),
            Spyder.Block3D((1, 1, 1), material="white"),
        )
    )

    marker = Spyder.Entity3D(
        "marker",
        (
            Spyder.NewMaterial("blue", color=(0, 0, 255)),
            Spyder.Circle(2, origin=(0, 0, 0.1), material="blue")
        )
    )
    del a


from bee.spyderhive.hivemaphive import hivemapinithive


def load_hive(hivemap):
    class loadedhive(hivemapinithive):
        hive = Spyder.Hivemap.fromfile(hivemap)

    return loadedhive


from bee.staticbind import staticbind_baseclass


class pandabind(dragonfly.event.bind,
                dragonfly.io.bind,
                dragonfly.sys.bind,
                dragonfly.scene.bind,
                dragonfly.time.bind,
                dragonfly.bind.bind):
    bind_entity = "relative"
    bind_keyboard = "indirect"


class pandalogicframe(bee.frame):
    name = bee.parameter("str")
    name_ = bee.get_parameter("name")

    do_trig_spawn = dragonfly.std.pushconnector("trigger")()
    trig_spawn = bee.output(do_trig_spawn.outp)

    v_panda = dragonfly.std.variable("id")(name_)
    t_set_panda = dragonfly.std.transistor("id")()
    connect(v_panda, t_set_panda)
    set_panda = bee.output(t_set_panda.outp)

    pandaicon_click = dragonfly.io.mouseareasensor(name_)
    connect(pandaicon_click, t_set_panda)
    connect(pandaicon_click, do_trig_spawn)


class pandalogichive(bee.frame):
    do_set_panda = dragonfly.std.pushconnector("id")()
    set_panda = bee.output(do_set_panda.outp)

    do_trig_spawn = dragonfly.std.pushconnector("trigger")()
    trig_spawn = bee.output(do_trig_spawn.outp)


class camerabind(staticbind_baseclass,
                 dragonfly.event.bind,
                 dragonfly.io.bind,
                 dragonfly.sys.bind,
                 dragonfly.scene.bind,
                 dragonfly.time.bind):
    pass


class myhive(dragonfly.pandahive.pandahive):
    canvas = dragonfly.pandahive.pandacanvas()
    mousearea = dragonfly.canvas.mousearea()
    raiser = bee.raiser()
    connect("evexc", raiser)

    camcenter = dragonfly.std.variable("id")("camcenter")
    connect(camcenter, ("camerabind", "bindname"))

    startsensor = dragonfly.sys.startsensor()
    cam = dragonfly.scene.get_camera()
    camparent = dragonfly.scene.unbound.parent()
    connect(cam, camparent.entityname)
    connect(camcenter, camparent.entityparentname)
    connect(startsensor, camparent)
    cphide = dragonfly.scene.unbound.hide()
    connect(camcenter, cphide)
    connect(startsensor, cphide)

    v_marker = dragonfly.std.variable("id")("marker")
    hide_marker = dragonfly.scene.unbound.hide()
    connect(v_marker, hide_marker)
    show_marker = dragonfly.scene.unbound.show()
    connect(v_marker, show_marker)
    parent_marker = dragonfly.scene.unbound.parent()
    connect(v_marker, parent_marker.entityname)
    connect(startsensor, hide_marker)

    pandaspawn = dragonfly.scene.spawn_actor_or_entity()
    v_panda = dragonfly.std.variable("id")("")
    connect(v_panda, pandaspawn)

    panda_id_gen = dragonfly.std.generator("id", id_generator)()
    panda_id = dragonfly.std.variable("id")("")
    t_panda_id_gen = dragonfly.std.transistor("id")()
    connect(panda_id_gen, t_panda_id_gen)
    connect(t_panda_id_gen, panda_id)
    random_matrix = dragonfly.std.generator(("object", "matrix"), random_matrix_generator)()
    w_spawn = dragonfly.std.weaver(("id", ("object", "matrix")))()
    connect(panda_id, w_spawn.inp1)
    connect(random_matrix, w_spawn.inp2)

    hivereg = dragonfly.bind.hiveregister()

    pandabinder = pandabind().worker()
    v_hivename = dragonfly.std.variable("id")("")
    w_bind = dragonfly.std.weaver(("id", "id"))()
    connect(panda_id, w_bind.inp1)
    connect(v_hivename, w_bind.inp2)
    t_bind = dragonfly.std.transistor("id")()
    connect(panda_id, t_bind)
    t_bind2 = dragonfly.std.transistor(("id", "id"))()
    connect(w_bind, t_bind2)
    connect(t_bind2, pandabinder.bind)

    sel = dragonfly.logic.selector()
    connect(t_bind, sel.register_and_select)
    selected = dragonfly.std.variable("id")("")
    connect(t_bind, selected)

    t_get_selected = dragonfly.logic.filter("trigger")()
    connect(sel.empty, t_get_selected)
    tt_get_selected = dragonfly.std.transistor("id")()
    do_select = dragonfly.std.pushconnector("trigger")()
    connect(t_get_selected.false, do_select)
    connect(do_select, tt_get_selected)
    connect(sel.selected, tt_get_selected)
    connect(tt_get_selected, selected)
    disp_sel = dragonfly.io.display("id")("Selected: ")
    connect(tt_get_selected, disp_sel)
    connect(selected, parent_marker.entityparentname)
    connect(do_select, show_marker)
    connect(do_select, parent_marker)

    key_tab = dragonfly.io.keyboardsensor_trigger("TAB")
    connect(key_tab, sel.select_next)
    connect(key_tab, t_get_selected)
    key_bsp = dragonfly.io.keyboardsensor_trigger("BACKSPACE")
    connect(key_bsp, sel.select_prev)
    connect(key_bsp, t_get_selected)

    kill = dragonfly.std.pushconnector("trigger")()
    t_kill = dragonfly.std.transistor("id")()
    connect(selected, t_kill)
    connect(t_kill, pandabinder.stop)
    remove = dragonfly.scene.unbound.remove_actor_or_entity()
    connect(t_kill, remove)
    disp_kill = dragonfly.io.display("id")("Killed: ")
    connect(t_kill, disp_kill)
    connect(kill, t_kill)
    connect(kill, sel.unregister)
    connect(kill, hide_marker)
    connect(kill, t_get_selected)
    testkill = dragonfly.logic.filter("trigger")()
    connect(sel.empty, testkill)
    connect(testkill.false, kill)
    key_k = dragonfly.io.keyboardsensor_trigger("K")
    connect(key_k, testkill)

    do_spawn = dragonfly.std.transistor(("id", ("object", "matrix")))()
    connect(w_spawn, do_spawn)
    connect(do_spawn, pandaspawn.spawn_matrix)
    trig_spawn = dragonfly.std.pushconnector("trigger")()
    connect(trig_spawn, t_panda_id_gen)
    connect(trig_spawn, do_spawn)
    connect(trig_spawn, t_bind)
    connect(trig_spawn, t_bind2)
    connect(trig_spawn, do_select)

    wininit = bee.init("window")
    wininit.camera.setPos(0, 45, 25)
    wininit.camera.setHpr(180, -20, 0)

    keyboardevents = dragonfly.event.sensor_match_leader("keyboard")
    add_head = dragonfly.event.add_head()
    head = dragonfly.convert.pull.duck("id", "event")()
    connect(selected, head)
    connect(keyboardevents, add_head)
    connect(head, add_head)
    connect(add_head, pandabinder.event)
  
