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


from dragonfly.canvas import box2d
from bee.mstr import mstr


class parameters: pass


class myscene(dragonfly.pandahive.spyderframe):
    a = Spyder.AxisSystem()
    a *= 0.25
    a.origin += (-8, 42, 0)
    env = Spyder.Model3D("models/environment", "egg", a)

    a = Spyder.AxisSystem()
    a *= 0.005
    pandaclass = Spyder.ActorClass3D("models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a,
                                     actorclassname="pandaclass")

    box = Spyder.Box2D(50, 470, 96, 96)
    icon = Spyder.Icon("pandaicon.png", "pandaicon", box, transparency=True)

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

    del a, box


class pandawalkhive(bee.inithive):
    animation = dragonfly.scene.bound.animation()
    walk = dragonfly.std.variable("str")("walk")
    connect(walk, animation.animation_name)

    key_w = dragonfly.io.keyboardsensor_trigger("W")
    connect(key_w, animation.loop)
    key_s = dragonfly.io.keyboardsensor_trigger("S")
    connect(key_s, animation.stop)

    setPos = dragonfly.scene.bound.setPos()
    setHpr = dragonfly.scene.bound.setHpr()

    interval = dragonfly.time.interval_time(18)
    connect(key_w, interval.start)
    connect(key_s, interval.pause)
    sequence = dragonfly.time.sequence(4)(8, 1, 8, 1)
    connect(interval.value, sequence.inp)

    ip1 = dragonfly.time.interpolation("Coordinate")((0, 0, 0), (0, -10, 0))
    connect(sequence.outp1, ip1)
    connect(ip1, setPos)
    connect(key_w, ip1.start)
    connect(key_s, ip1.stop)

    ip2 = dragonfly.time.interpolation("Coordinate")((0, 0, 0), (180, 0, 0))
    connect(sequence.outp2, ip2)
    connect(ip2, setHpr)
    connect(key_w, ip2.start)
    connect(key_s, ip2.stop)

    ip3 = dragonfly.time.interpolation("Coordinate")((0, -10, 0), (0, 0, 0))
    connect(sequence.outp3, ip3)
    connect(ip3, setPos)
    connect(key_w, ip3.start)
    connect(key_s, ip3.stop)

    ip4 = dragonfly.time.interpolation("Coordinate")((180, 0, 0), (0, 0, 0))
    connect(sequence.outp4, ip4)
    connect(ip4, setHpr)
    connect(key_w, ip4.start)
    connect(key_s, ip4.stop)

    connect(ip4.reach_end, interval.start)


from bee.staticbind import staticbind_baseclass


class pandabind(dragonfly.event.bind,
                dragonfly.io.bind,
                dragonfly.sys.bind,
                dragonfly.scene.bind,
                dragonfly.time.bind,
                dragonfly.bind.bind):
    bind_entity = "relative"
    bind_keyboard = "indirect"


class camerabindhive(bee.inithive):
    interval = dragonfly.time.interval_time(30)
    sequence = dragonfly.time.sequence(2)(1, 1)
    connect(interval.value, sequence.inp)
    startsensor = dragonfly.sys.startsensor()

    ip1 = dragonfly.time.interpolation("Coordinate")((180, -20, 0), (360, -20, 0))
    ip2 = dragonfly.time.interpolation("Coordinate")((0, -20, 0), (180, -20, 0))
    connect(sequence.outp1, ip1.inp)
    connect(sequence.outp2, ip2.inp)

    connect(startsensor, interval.start)
    connect(startsensor, ip1.start)

    connect(ip1.reach_end, ip1.stop)
    connect(ip1.reach_end, ip2.start)
    connect(ip2.reach_end, ip2.stop)
    connect(ip2.reach_end, ip1.start)

    connect(ip2.reach_end, interval.start)

    sethpr = dragonfly.scene.bound.setHpr()
    connect(ip1, sethpr)
    connect(ip2, sethpr)


class camerabind(staticbind_baseclass,
                 dragonfly.event.bind,
                 dragonfly.io.bind,
                 dragonfly.sys.bind,
                 dragonfly.scene.bind,
                 dragonfly.time.bind):
    hive = camerabindhive


class myhive(dragonfly.pandahive.pandahive):
    canvas = dragonfly.pandahive.pandacanvas()
    mousearea = dragonfly.canvas.mousearea()
    raiser = bee.raiser()
    connect("evexc", raiser)

    camerabind = camerabind().worker()
    camcenter = dragonfly.std.variable("id")("camcenter")
    connect(camcenter, camerabind.bindname)

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

    pandaspawn = dragonfly.scene.spawn_actor()
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
    c_hivereg = bee.configure("hivereg")

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

    #First panda
    v_panda1 = dragonfly.std.variable("id")("pandaclass")
    set_panda1 = dragonfly.std.transistor("id")()
    connect(v_panda1, set_panda1)
    connect(set_panda1, v_panda)

    c_hivereg.register_hive("pandawalk", pandawalkhive)
    v_hivename1 = dragonfly.std.variable("id")("pandawalk")
    set_hivename1 = dragonfly.std.transistor("id")()
    connect(v_hivename1, set_hivename1)
    connect(set_hivename1, v_hivename)

    pandaicon_click = dragonfly.io.mouseareasensor("pandaicon")
    connect(pandaicon_click, set_panda1)
    connect(pandaicon_click, set_hivename1)
    connect(pandaicon_click, trig_spawn)

    myscene = myscene(
        scene="scene",
        canvas=canvas,
        mousearea=mousearea,
    )

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


main = myhive().getinstance()
main.build("main")
main.place()
main.close()
main.init()

main.run()
