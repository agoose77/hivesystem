from hiveguilib.HBlender import register_hivemap, register_workermap, register_spydermap
register_hivemap.register()
register_workermap.register()
register_spydermap.register()

import bee
from hiveguilib.worker import WorkerFinder, WorkerBuilder
import sys
wb = WorkerBuilder()
wf = WorkerFinder(["dragonfly"], sys.path)
#print(wf.workers.keys())
#print(wf.metaworkers.keys())
#print(wf.hivemapworkers.keys())
#print(wf.spydermapworkers.keys())
#print(wf.drones.keys())
#print(wf.spyderhives.keys())
#print(wf.typelist)

from hiveguilib.HBlender import register_nodeclass
names = [
  "dragonfly.logic.selector",
  "dragonfly.logic.cycle"
]  
for name in wf.workers.keys():
  wb.build_worker(name, wf.workers[name])

  #for now, just register the worker attribs as Blender class, although this is not as it is done in HiveGUI...
  wi = wb._workers[name].get_workerinstance()
  attribs = wi.profiles["default"][0]
  register_nodeclass.register_nodeclass(name, attribs)
for name in wf.metaworkers.keys():
  wb.build_metaworker(name, wf.metaworkers[name])

  register_nodeclass.register_nodeclass(name, [])
  
register_nodeclass.finalize()

