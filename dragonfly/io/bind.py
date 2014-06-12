import libcontext
from bee.bind import *
from ..event.bind import eventlistener

class bind(bind_baseclass):
  bind_keyboard = bindparameter("direct")
  binder("bind_keyboard", False, None)
  binder("bind_keyboard", "direct", eventlistener("keyboard"), "bindname")
  binder("bind_keyboard", "direct", pluginbridge(("evin",("input","keyboard"))))
  binder("bind_keyboard", "indirect", pluginbridge(("evin",("input","keyboard"))))
  bind_mouse = bindparameter(False)
  binder("bind_mouse", False, None)
  binder("bind_mouse", "direct", eventlistener("mouse"), "bindname")
  binder("bind_mouse", "direct", pluginbridge(("evin",("input","mouse"))))
  binder("bind_mouse", "indirect", pluginbridge(("evin",("input","mouse"))))
  bind_display = bindparameter(True)
  binder("bind_display",False,None)
  binder("bind_display",True,pluginbridge("display"))
  bind_watch = bindparameter(True)
  binder("bind_watch",False,None)
  binder("bind_watch",True,pluginbridge("watch"))  
