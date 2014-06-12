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


class myhive(dragonfly.pandahive.pandahive):
    raiser = bee.raiser()
    connect("evexc", raiser)

    animation = dragonfly.scene.unbound.animation()
    pandaid = dragonfly.std.variable("id")("mypanda")
    walk = dragonfly.std.variable("str")("walk")
    connect(pandaid, animation.actor)
    connect(walk, animation.animation_name)

    key_w = dragonfly.io.keyboardsensor_trigger("W")
    connect(key_w, animation.loop)
    key_s = dragonfly.io.keyboardsensor_trigger("S")
    connect(key_s, animation.stop)

    pandaspawn = dragonfly.scene.spawn_actor()
    v_panda = dragonfly.std.variable("id")("pandaclass")
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


main = myhive().getinstance()
main.build("main")

main.scene.import_mesh_EGG("models/environment")
a = NodePath("")
a.setScale(0.25)
a.setPos(-8, 42, 0)
mat = a.getMat()
m = (mat.getRow3(3), mat.getRow3(0), mat.getRow3(1), mat.getRow3(2))
main.scene.add_model_MATRIX(matrix=m)

main.scene.import_mesh_EGG("models/panda-model")
a = NodePath("")
a.setScale(0.005)
mat = a.getMat()
m = (mat.getRow3(3), mat.getRow3(0), mat.getRow3(1), mat.getRow3(2))
main.scene.add_actor_MATRIX(matrix=m, entityname="mypanda")
main.scene.import_mesh_EGG("models/panda-walk4")
main.scene.add_animation("walk")

main.scene.import_mesh_EGG("models/panda-model")
a = NodePath("")
a.setScale(0.005)
mat = a.getMat()
m = (mat.getRow3(3), mat.getRow3(0), mat.getRow3(1), mat.getRow3(2))
main.scene.add_actorclass_MATRIX(matrix=m, actorclassname="pandaclass")
main.scene.import_mesh_EGG("models/panda-walk4")
main.scene.add_animation("walk")

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
