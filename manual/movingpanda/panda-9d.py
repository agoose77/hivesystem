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

### random matrix generator
from random import random
def random_matrix_generator():
  while 1:
    a = Spyder.AxisSystem()
    a.rotateZ(360*random())
    a.origin=Spyder.Coordinate(15*random()-7.5,15*random()-7.5, 0)
    yield dragonfly.scene.matrix(a, "AxisSystem")

def id_generator():
  n = 0
  while 1:
    yield "spawnedpanda" + str(n)

pandadict = {} #global variable...

#First panda class
a = Spyder.AxisSystem()
a *= 0.005
data = "models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a
box = Spyder.Box2D(50,470,96,96)
image = "pandaicon.png", True
pandadict["pandaclass"] = ("actor", data, box, image)

#Second panda class
a = Spyder.AxisSystem()
a *= 0.002
data = "models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a
box = Spyder.Box2D(200,500,48,48)
image = "pandaicon.png", True
pandadict["pandaclass2"] = ("actor", data, box, image)

#Third panda class
a = Spyder.AxisSystem()
a *= 0.3
data = "models/panda", "egg", [], a
box = Spyder.Box2D(280,480,144,112)
image = "pandaicon2.png", True
pandadict["pandaclass3"] = ("model", data, box, image)

def generate_pandascene():
  class pandascenehive(dragonfly.pandahive.spyderframe):
    for name in pandadict:
      mode, data, box, image = pandadict[name]
      model, modelformat, animations, a = data
      if mode == "actor":
        obj = Spyder.ActorClass3D(model,modelformat,animations,a,actorclassname=name)
      elif mode == "model":
        model = Spyder.Model3D(model, modelformat, a)
        obj = Spyder.EntityClass3D(name,[model])
      else:
        raise ValueError(mode)
      locals()[name+"_obj"] = obj
      
      im, transp = image
      locals()[name+"_icon"] = Spyder.Icon(im,name,box,transparency=transp)

    del name
    del model, modelformat, animations, a, obj
    del mode, data, box, image
    del im, transp
  return pandascenehive
  
class myscene(dragonfly.pandahive.spyderframe):
  a = Spyder.AxisSystem()
  a *= 0.25
  a.origin += (-8,42,0)
  env = Spyder.Model3D("models/environment", "egg", a)
 
  a = Spyder.AxisSystem()
  a *= 0.005
  mypanda = Spyder.Actor3D("models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a,entityname="mypanda")

  pandascene = generate_pandascene()(scene="scene",canvas="canvas",mousearea="mousearea")
  del a

def generate_pandalogic():
  class pandalogichive(bee.frame):
    c_inp = dragonfly.std.pullconnector(("id",("object","matrix")))()
    inp = bee.antenna(c_inp.inp)
    
    for name in pandadict:
      mode, data, box, image = pandadict[name]
      if mode == "actor":
        spawn = dragonfly.scene.spawn_actor() 
      elif mode == "model":
        spawn = dragonfly.scene.spawn() 
      else:
        raise ValueError(mode)
      
      locals()["v_panda_"+name] = dragonfly.std.variable("id")(name)
      locals()["pandaspawn_"+name] = spawn
      connect("v_panda_"+name, spawn)
      locals()["do_spawn_"+name] = dragonfly.std.transistor(("id",("object","matrix")))()
      connect(c_inp, "do_spawn_"+name)
      connect("do_spawn_"+name, spawn.spawn_matrix)

      locals()["pandaicon_click_"+name] = dragonfly.io.mouseareasensor(name)
      connect("pandaicon_click_"+name, "do_spawn_"+name)
      
    del name
    del mode, data, box, image
    del spawn
  return pandalogichive
  
class myhive(dragonfly.pandahive.pandahive):
  pandaname = "mypanda"
  pandaname_ = bee.attribute("pandaname")
  
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

  random_matrix = dragonfly.std.generator(("object","matrix"), random_matrix_generator)()
  panda_id = dragonfly.std.generator("id", id_generator)()

  w_spawn = dragonfly.std.weaver(("id",("object","matrix")))()
  connect(panda_id, w_spawn.inp1)
  connect(random_matrix, w_spawn.inp2)
  
  pandalogic = generate_pandalogic()()
  connect(w_spawn, pandalogic.inp)

  myscene = myscene(
             scene="scene",
	     canvas = canvas,
	     mousearea = mousearea,
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
