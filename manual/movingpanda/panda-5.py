import dragonfly
import dragonfly.pandahive
import bee
from bee import connect

import math, functools

from panda3d.core import NodePath

import dragonfly.scene.unbound
import dragonfly.std
import dragonfly.io

# ## random matrix generator
from random import random


def random_matrix_generator():
    while 1:
        a = NodePath("")
        a.setHpr(360 * random(), 0, 0)
        a.setPos(15 * random() - 7.5, 15 * random() - 7.5, 0)
        yield dragonfly.scene.matrix(a, "NodePath")


def id_generator():
    n = 0
    while 1:
        yield "spawnedpanda" + str(n)


class myscene(bee.frame):
    pandaclassname_ = bee.ParameterGetter("pandaclassname")
    pandaname_ = bee.ParameterGetter("pandaname")

    c1 = bee.Configure("scene")
    c1.import_mesh_EGG("models/environment")
    a = NodePath("")
    a.setScale(0.25)
    a.setPos(-8, 42, 0)
    mat = a.getMat()
    m = (mat.getRow3(3), mat.getRow3(0), mat.getRow3(1), mat.getRow3(2))
    c1.add_model_MATRIX(matrix=m)

    c2 = bee.Configure("scene")
    c2.import_mesh_EGG("models/panda-model")
    a = NodePath("")
    a.setScale(0.005)
    mat = a.getMat()
    m = (mat.getRow3(3), mat.getRow3(0), mat.getRow3(1), mat.getRow3(2))
    c2.add_actor_MATRIX(matrix=m, entityname=pandaname_)
    c2.import_mesh_EGG("models/panda-walk4")
    c2.add_animation("walk")

    c3 = bee.Configure("scene")
    c3.import_mesh_EGG("models/panda-model")
    a = NodePath("")
    a.setScale(0.005)
    mat = a.getMat()
    m = (mat.getRow3(3), mat.getRow3(0), mat.getRow3(1), mat.getRow3(2))
    c3.add_actorclass_MATRIX(matrix=m, actorclassname=pandaclassname_)
    c3.import_mesh_EGG("models/panda-walk4")
    c3.add_animation("walk")

    del a, m, mat


class myhive(dragonfly.pandahive.pandahive):
    pandaname = "mypanda"
    pandaname_ = bee.attribute("pandaname")
    pandaclassname = "pandaclass"
    pandaclassname_ = bee.attribute("pandaclassname")

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

    myscene = myscene(
        scene="scene",
        pandaname=pandaname_,
        pandaclassname=pandaclassname_,
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
