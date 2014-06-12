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
from bee.mstr import mstr


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


main = myhive().getinstance()
main.build("main")
main.place()
main.close()
main.init()

from direct.task import Task


def spinCameraTask(camera, task):
    angleDegrees = task.time * 30.0
    angleRadians = angleDegrees * (math.pi / 180.0)
    camera.setPos(20 * math.sin(angleRadians), -20.0 * math.cos(angleRadians), 3)
    camera.setHpr(angleDegrees, 0, 0)
    return Task.cont


main.window.taskMgr.add(functools.partial(spinCameraTask, main.window.camera), "SpinCameraTask")

main.run()
