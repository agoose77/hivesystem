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
from bee.stringvalue import StringValue


class parameters: pass


class myscene(dragonfly.pandahive.spyderframe):
    a = Spyder.AxisSystem()
    a *= 0.25
    a.origin += (-8, 42, 0)
    env = Spyder.Model3D("models/environment", "egg", a)

    #First panda
    a = Spyder.AxisSystem()
    a *= 0.005
    pandaclass = Spyder.ActorClass3D("models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a,
                                     actorclassname="pandaclass")

    box = Spyder.Box2D(50, 470, 96, 96)
    icon = Spyder.Icon("pandaicon.png", "pandaicon", box, transparency=True)

    #Second panda
    a = Spyder.AxisSystem()
    a *= 0.002
    pandaclass2 = Spyder.ActorClass3D("models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a,
                                      actorclassname="pandaclass2")

    box = Spyder.Box2D(200, 500, 48, 48)
    icon2 = Spyder.Icon("pandaicon.png", "pandaicon2", box, transparency=True)

    #Third panda
    a = Spyder.AxisSystem()
    a *= 0.3
    model = Spyder.Model3D("models/panda", "egg", a)
    pandaclass3 = Spyder.EntityClass3D("pandaclass3", [model])

    box = Spyder.Box2D(280, 480, 144, 112)
    icon3 = Spyder.Icon("pandaicon2.png", "pandaicon3", box, transparency=True)

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

    del a, box, model


from bee.spyderhive.hivemaphive import hivemapinithive


class pandawalkhive(hivemapinithive):
    pandahivemap = Spyder.Hivemap.fromfile("pandawalk.web")


class pandawalkhive2(hivemapinithive):
    pandahivemap = Spyder.Hivemap.fromfile("pandawalk2.web")


from jumpworker2 import jumpworker2


class jumpworkerhive(bee.frame):
    height = bee.Parameter("float")
    duration = bee.Parameter("float")

    i = dragonfly.time.interval_time(time=bee.ParameterGetter("duration"))
    startconnector = dragonfly.std.pushconnector("trigger")()
    connect(startconnector, i.start)

    start = bee.Antenna(startconnector.inp)

    jump = jumpworker2(height=bee.ParameterGetter("height"))
    connect(i, jump)
    t_jump = dragonfly.std.transistor("float")()
    connect(jump, t_jump)
    dojump = dragonfly.scene.bound.setZ()
    connect(t_jump, dojump)

    tick = dragonfly.io.ticksensor(False)
    connect(tick, t_jump)
    connect(startconnector, tick.start)
    connect(i.reach_end, tick.stop)


class pandajumphive(bee.inithive):
    ksp = dragonfly.io.keyboardsensor_trigger("SPACE")
    jump = jumpworkerhive(height=4.0, duration=0.7)
    connect(ksp, jump)


from bee.staticbind import staticbind_baseclass


class pandabind(dragonfly.event.bind,
                dragonfly.io.bind,
                dragonfly.sys.bind,
                dragonfly.scene.bind,
                dragonfly.time.bind,
                dragonfly.bind.bind):
    bind_entity = "relative"
    bind_keyboard = "indirect"


class camerabindhive(hivemapinithive):
    camera_hivemap = Spyder.Hivemap.fromfile("camera.web")


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
    c_hivereg = bee.Configure("hivereg")

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

    #Second panda
    v_panda2 = dragonfly.std.variable("id")("pandaclass2")
    set_panda2 = dragonfly.std.transistor("id")()
    connect(v_panda2, set_panda2)
    connect(set_panda2, v_panda)

    c_hivereg.register_hive("pandawalk2", pandawalkhive2)
    v_hivename2 = dragonfly.std.variable("id")("pandawalk2")
    set_hivename2 = dragonfly.std.transistor("id")()
    connect(v_hivename2, set_hivename2)
    connect(set_hivename2, v_hivename)

    pandaicon2_click = dragonfly.io.mouseareasensor("pandaicon2")
    connect(pandaicon2_click, set_panda2)
    connect(pandaicon2_click, set_hivename2)
    connect(pandaicon2_click, trig_spawn)

    #Third panda
    v_panda3 = dragonfly.std.variable("id")("pandaclass3")
    set_panda3 = dragonfly.std.transistor("id")()
    connect(v_panda3, set_panda3)
    connect(set_panda3, v_panda)

    c_hivereg.register_hive("pandajump", pandajumphive)
    v_hivename3 = dragonfly.std.variable("id")("pandajump")
    set_hivename3 = dragonfly.std.transistor("id")()
    connect(v_hivename3, set_hivename3)
    connect(set_hivename3, v_hivename)

    pandaicon3_click = dragonfly.io.mouseareasensor("pandaicon3")
    connect(pandaicon3_click, set_panda3)
    connect(pandaicon3_click, set_hivename3)
    connect(pandaicon3_click, trig_spawn)

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
