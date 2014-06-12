import dragonfly
import bee
from bee import *
from bee.spyderhive.hivemaphive import hivemapframe
import Spyder

from dragonfly.commandhive import commandhive, commandapp

from panda3d.core import getModelPath
import os

getModelPath().prependPath(os.getcwd())

from bee import hivemodule


class myhivemapframe(hivemapframe):
    hm = Spyder.Hivemap.fromfile("tut-worker-4b.web")


class myapp(commandapp):
    def on_tick(self):
        taskMgr.step()
        taskMgr.step()


class myhive(commandhive):
    _hivecontext = hivemodule.appcontext(myapp)

    h = myhivemapframe()

    raiser = bee.raiser()
    bee.connect("evexc", raiser)


m = myhive().getinstance()
m.build("m")
m.place()
m.close()

m.init()

m.run()

