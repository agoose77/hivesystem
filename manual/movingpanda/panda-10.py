import dragonfly
import dragonfly.pandahive
import bee
from bee import connect

import math, functools

from panda3d.core import NodePath

import dragonfly.scene.unbound
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


class myhive(dragonfly.pandahive.pandahive):
    pandaname = "mypanda"
    pandaname_ = bee.attribute("pandaname")
    pandaclassname = "pandaclass"
    pandaclassname_ = bee.attribute("pandaclassname")

    canvas = dragonfly.pandahive.pandacanvas()
    mousearea = dragonfly.canvas.mousearea()
    raiser = bee.raiser()
    connect("evexc", raiser)

    animation = dragonfly.scene.unbound.animation()
    pandaid = dragonfly.std.variable("id")(pandaname_)
    walk = dragonfly.std.variable("str")("walk")
    connect(pandaid, animation.actor)
    connect(walk, animation.animation_name)

    key_w = dragonfly.io.keyboardsensor_trigger("W")
    connect(key_w, animation.loop)
    key_s = dragonfly.io.keyboardsensor_trigger("S")
    connect(key_s, animation.stop)

    setPos = dragonfly.scene.unbound.setPos()
    connect(pandaid, setPos)

    interval = dragonfly.time.interval_time(8)
    connect(key_w, interval.start)
    connect(key_s, interval.pause)
    ip = dragonfly.time.interpolation("Coordinate")((0, 0, 0), (0, -10, 0))
    connect(interval.value, ip)
    connect(ip, setPos)
    connect(key_w, ip.start)
    connect(key_s, ip.stop)

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
