import dragonfly
import dragonfly.pandahive
import bee
from bee import connect

import math, functools

from panda3d.core import NodePath


class myhive(dragonfly.pandahive.pandahive):
    raiser = bee.raiser()
    connect("evexc", raiser)


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
main.scene.add_actor_MATRIX(matrix=m)
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
