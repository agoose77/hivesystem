import dragonfly
import dragonfly.pandahive
import bee
from bee import connect

import math, functools

from panda3d.core import NodePath

import dragonfly.scene.unbound
import dragonfly.std
import dragonfly.io


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
