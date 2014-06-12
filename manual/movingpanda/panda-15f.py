from pandalib import myhive, myscene, pandalogichive, pandalogicframe, load_hive, camerabind
import bee, dragonfly
from bee import connect
import Spyder

pandadict = {} #temporary variable...

#First panda class
a = Spyder.AxisSystem()
a *= 0.005
data = "models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a
box = Spyder.Box2D(50,470,96,96)
image = "pandaicon.png", True
hivemap = "pandawalk.web"
pandadict["pandaclass"] = ("actor", data, box, image, hivemap)

#Second panda class
a = Spyder.AxisSystem()
a *= 0.002
data = "models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a
box = Spyder.Box2D(200,500,48,48)
image = "pandaicon.png", True
hivemap = "pandawalk2.web"
pandadict["pandaclass2"] = ("actor", data, box, image, hivemap)

#Third panda class
a = Spyder.AxisSystem()
a *= 0.3
data = "models/panda", "egg", [], a
box = Spyder.Box2D(280,480,144,112)
image = "pandaicon2.png", True
hivemap = "pandajump.web"
pandadict["pandaclass3"] = ("model", data, box, image, hivemap)

def generate_pandasceneframe(name, panda):
  class pandasceneframe(dragonfly.pandahive.spyderframe):
    mode, data, box, image, hivemap = panda
    model, modelformat, animations, a = data
    if mode == "actor":
      obj = Spyder.ActorClass3D(model,modelformat,animations,a,actorclassname=name)
    elif mode == "model":
      model = Spyder.Model3D(model, modelformat, a)
      obj = Spyder.EntityClass3D(name,[model])
    else:
      raise ValueError(mode)
      
    im, transp = image
    icon = Spyder.Icon(im,name,box,transparency=transp)

    del model, modelformat, animations, a
    del mode, data, box, image, hivemap
    del im, transp
  return pandasceneframe

class myscene2(myscene):
  pass
    
class pandalogichive2(pandalogichive):
  pass

from bee.spyderhive.hivemaphive import hivemapinithive
class camerabindhive(hivemapinithive):
  pass
  
class camerabind2(camerabind):
  hive = camerabindhive

class pandadictdrone(bee.combodrone):
  def __init__(self, pandadict):
    self.pandadict = pandadict
  def make_combo(self):
    pandas = []
    c_hivereg = bee.configure("hivereg")    
    pandalogics = [c_hivereg]
    for name in pandadict:
      panda = pandadict[name]
      pandasceneframe = generate_pandasceneframe(name,panda)(scene="scene",canvas="canvas",mousearea="mousearea")
      pandas.append(pandasceneframe)

      mode, data, box, image, hivemap = panda
      hive = load_hive(hivemap)
      c_hivereg.register_hive(name, hive)
      p = pandalogicframe(name)
      c1 = connect(p.set_panda, "do_set_panda")
      c2 = connect(p.trig_spawn, "do_trig_spawn")
      pandalogics += [p,c1,c2]  
    return {"myscene":pandas, "pandalogic":pandalogics}
  
class mycombohive(bee.combohive):
  pandadict = pandadict
  pandadict_ = bee.attribute("pandadict")
  
  cb1 = pandadictdrone(pandadict_)
  camerahive = Spyder.Hivemap.fromfile("camera.web")
  cb2 = Spyder.Combobee((("camerabindhive",camerahive),))
  #or: cb2 = bee.combodronewrapper({"camerabindhive":camerahive})
  del camerahive

class mainhive(myhive):
  pandalogic = pandalogichive2(hivereg="hivereg")
  connect(pandalogic.set_panda, "v_panda")
  connect(pandalogic.set_panda, "v_hivename")
  connect(pandalogic.trig_spawn, "trig_spawn")

  camerabind = camerabind2().worker()

  myscene = myscene2(
             scene="scene",
	     canvas = "canvas",
	     mousearea = "mousearea",	     
	    )
  mycombo = mycombohive(
             myscene=myscene,
	     pandalogic=pandalogic,
	     camerabindhive=camerabind.hive
           )
  
main = mainhive().getinstance()  
main.build("main")
main.place()
main.close()
main.init()

main.run()
