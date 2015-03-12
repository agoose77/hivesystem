import dragonfly
import dragonfly.pandahive
import bee
from bee import connect

import math, functools

from panda3d.core import NodePath

import dragonfly.scene.unbound, dragonfly.scene.bound
import dragonfly.std
import dragonfly.io
import dragonfly.canvas

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

    a = Spyder.AxisSystem()
    a *= 0.005
    mypanda = Spyder.Actor3D("models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a,
                             entityname="mypanda")

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


class pandawalkbind(staticbind_baseclass,
                    dragonfly.event.bind,
                    dragonfly.io.bind,
                    dragonfly.sys.bind,
                    dragonfly.scene.bind,
                    dragonfly.time.bind):
    hive = pandawalkhive


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
    pandaname = "mypanda"
    pandaname_ = bee.attribute("pandaname")
    pandaclassname = "pandaclass"
    pandaclassname_ = bee.attribute("pandaclassname")

    canvas = dragonfly.pandahive.pandacanvas()
    mousearea = dragonfly.canvas.mousearea()
    raiser = bee.raiser()
    connect("evexc", raiser)

    z_pandawalk = pandawalkbind().worker()
    pandaid = dragonfly.std.variable("id")(pandaname_)
    connect(pandaid, z_pandawalk.bindname)

    camerabind = camerabind().worker()
    camcenter = dragonfly.std.variable("id")("camcenter")
    connect(camcenter, camerabind.bindname)

    startsensor = dragonfly.sys.startsensor()
    cam = dragonfly.scene.get_camera()
    camparent = dragonfly.scene.unbound.parent()
    connect(cam, camparent.entityname)
    connect(camcenter, camparent.entityparentname)
    connect(startsensor, camparent)

    pandaspawn = dragonfly.scene.spawn_actor()
    v_panda = dragonfly.std.variable("id")(pandaclassname_)
    connect(v_panda, pandaspawn)

    panda_id = dragonfly.std.generator("id", id_generator)()
    random_matrix = dragonfly.std.generator(("object", "matrix"), random_matrix_generator)()
    w_spawn = dragonfly.std.weaver(("id", ("object", "matrix")))()
    connect(panda_id, w_spawn.inp1)
    connect(random_matrix, w_spawn.inp2)

    do_spawn = dragonfly.std.transistor(("id", ("object", "matrix")))()
    connect(w_spawn, do_spawn)
    connect(do_spawn, pandaspawn.spawn_matrix)
    key_z = dragonfly.io.keyboardsensor_trigger("Z")
    connect(key_z, do_spawn)

    pandaicon_click = dragonfly.io.mouseareasensor("pandaicon")
    connect(pandaicon_click, do_spawn)

    myscene = myscene(
        scene="scene",
        canvas=canvas,
        mousearea=mousearea,
    )

    wininit = bee.init("window")
    wininit.camera.setPos(0, 45, 25)
    wininit.camera.setHpr(180, -20, 0)


main = myhive().getinstance()
main.build("main")
main.place()
main.close()
main.init()

main.run()
