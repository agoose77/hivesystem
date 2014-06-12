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


pandadict = {}  #global variable...

#First panda class
a = Spyder.AxisSystem()
a *= 0.005
data = "models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a
box = Spyder.Box2D(50, 470, 96, 96)
image = "pandaicon.png", True
hivemap = "pandawalk.web"
pandadict["pandaclass"] = ("actor", data, box, image, hivemap)

#Second panda class
a = Spyder.AxisSystem()
a *= 0.002
data = "models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a
box = Spyder.Box2D(200, 500, 48, 48)
image = "pandaicon.png", True
hivemap = "pandawalk2.web"
pandadict["pandaclass2"] = ("actor", data, box, image, hivemap)

#Third panda class
a = Spyder.AxisSystem()
a *= 0.3
data = "models/panda", "egg", [], a
box = Spyder.Box2D(280, 480, 144, 112)
image = "pandaicon2.png", True
hivemap = "pandajump.web"
pandadict["pandaclass3"] = ("model", data, box, image, hivemap)

from dragonfly.canvas import box2d
from bee.mstr import mstr


class parameters: pass


def generate_pandasceneframe(name, panda):
    class pandasceneframe(dragonfly.pandahive.spyderframe):
        mode, data, box, image, hivemap = panda
        model, modelformat, animations, a = data
        if mode == "actor":
            obj = Spyder.ActorClass3D(model, modelformat, animations, a, actorclassname=name)
        elif mode == "model":
            model = Spyder.Model3D(model, modelformat, a)
            obj = Spyder.EntityClass3D(name, [model])
        else:
            raise ValueError(mode)

        im, transp = image
        icon = Spyder.Icon(im, name, box, transparency=transp)

        del model, modelformat, animations, a
        del mode, data, box, image, hivemap
        del im, transp

    return pandasceneframe


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

    for name in pandadict:
        panda = pandadict[name]
        pandasceneframe = generate_pandasceneframe(name, panda)(scene="scene", canvas="canvas", mousearea="mousearea")
        locals()["pandasceneframe_%s" % name] = pandasceneframe

    del a, name, panda, pandasceneframe


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


def generate_pandalogic():
    class pandalogichive(bee.frame):
        do_set_panda = dragonfly.std.pushconnector("id")()
        set_panda = bee.output(do_set_panda.outp)

        do_trig_spawn = dragonfly.std.pushconnector("trigger")()
        trig_spawn = bee.output(do_trig_spawn.outp)

        c_hivereg = bee.configure("hivereg")

        for name in pandadict:
            mode, data, box, image, hivemap = pandadict[name]

            hive = load_hive(hivemap)
            c_hivereg.register_hive(name, hive)

            locals()["v_panda_" + name] = dragonfly.std.variable("id")(name)
            locals()["set_panda_" + name] = dragonfly.std.transistor("id")()
            connect("v_panda_" + name, "set_panda_" + name)
            connect("set_panda_" + name, do_set_panda)

            locals()["pandaicon_click_" + name] = dragonfly.io.mouseareasensor(name)
            connect("pandaicon_click_" + name, "set_panda_" + name)
            connect("pandaicon_click_" + name, do_trig_spawn)

        del name, hive
        del mode, data, box, image, hivemap

    return pandalogichive


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

    pandalogic = generate_pandalogic()(hivereg="hivereg")
    connect(pandalogic.set_panda, v_panda)
    connect(pandalogic.set_panda, v_hivename)
    connect(pandalogic.trig_spawn, trig_spawn)

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
