import spyder
import movingpanda_datamodel
import Spyder

pandadict = {}

# First panda class
a = Spyder.AxisSystem()
a *= 0.005
data = "models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a
box = Spyder.Box2D(50, 470, 96, 96)
image = "pandaicon.png", True
hivemap = "pandawalk.web"
pandadict["pandaclass"] = ("actor", data, box, image, hivemap)

#Second panda class
a = Spyder.AxisSystem()
a *= 0.002
data = "models/panda-model", "egg", [("walk", "models/panda-walk4", "egg")], a
box = Spyder.Box2D(200, 500, 48, 48)
image = "pandaicon.png", True
hivemap = "pandawalk2.web"
pandadict["pandaclass2"] = ("actor", data, box, image, hivemap)

#Third panda class
a = Spyder.AxisSystem()
a *= 0.3
data = "models/panda", "egg", [], a
box = Spyder.Box2D(280, 480, 144, 112)
image = "pandaicon2.png", True
hivemap = "pandajump.web"
pandadict["pandaclass3"] = ("model", data, box, image, hivemap)

#Build the Spyder file from the dict
mps = Spyder.MovingPandaArray()
for name in sorted(pandadict.keys()):
    mode, data, box, image, hivemap = pandadict[name]
    model, modelformat, animations, a = data
    if mode == "actor":
        obj = Spyder.ActorClass3D(model, modelformat, animations, a, actorclassname=name)
    elif mode == "model":
        model = Spyder.Model3D(model, modelformat, a)
        obj = Spyder.EntityClass3D(name, [model])
    else:
        raise ValueError(mode)

    mp = Spyder.MovingPanda(
        name,
        hivemap,
        mode,
        [obj],
        image[0],
        box,
        image[1],
    )
    mps.append(mp)
mps.tofile("panda-final.web")
