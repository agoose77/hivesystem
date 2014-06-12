from pandalib import myhive, myscene, pandalogichive, pandalogicframe, load_hive, camerabind
import bee, dragonfly
from bee import connect

import spyder
import movingpanda_datamodel
import Spyder

class myscene2(myscene):
  pass
    
class pandalogichive2(pandalogichive):
  pass

from bee.spyderhive.hivemaphive import hivemapinithive
class camerabindhive(hivemapinithive):
  pass
  
class camerabind2(camerabind):
  hive = camerabindhive

def load_panda(mpanda):
  pandas = []  
  c_hivereg = bee.configure("hivereg")
  pandalogics = [c_hivereg]  

  pandas.append(mpanda.model[0])
  icon = Spyder.Icon(
    mpanda.image,
    mpanda.pname,
    mpanda.box,
    transparency=mpanda.transparency
  )
  pandas.append(icon)

  hive = load_hive(mpanda.hivemap)
  c_hivereg.register_hive(mpanda.pname, hive)
  p = pandalogicframe(mpanda.pname)
  c1 = connect(p.set_panda, "do_set_panda")
  c2 = connect(p.trig_spawn, "do_trig_spawn")
  pandalogics += [p,c1,c2]  
  
  return {"myscene":pandas,"pandalogic":pandalogics}  

from bee.spyderhive import SpyderMethod  
class mycombohive(bee.combohive):
  SpyderMethod("make_combo", "MovingPanda", load_panda)
  
  movingpandas = Spyder.MovingPandaArray.fromfile("panda-final.web")
  
  camerahive = Spyder.Hivemap.fromfile("camera.web")
  cb2 = Spyder.Combobee((("camerabindhive",camerahive),))
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
