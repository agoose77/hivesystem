import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from bee.bind import *

class entitybinder(binderdrone):
  def set_entityfunc(self, entityfunc):
    self._get_entity = entityfunc
  def set_entityfunc_nodepath(self, entityfunc_nodepath):
    self._get_entity_nodepath = entityfunc_nodepath    
  def set_entityfunc_axissystem(self, entityfunc_axissystem):
    self._get_entity_axissystem = entityfunc_axissystem        
  def bind(self, binderworker, bindname):
    libcontext.plugin("entity", plugin_supplier(lambda: self._get_entity(bindname)))
    libcontext.plugin(("entity","NodePath"), plugin_supplier(lambda: self._get_entity_nodepath(bindname)))
    libcontext.plugin(("entity","AxisSystem"), plugin_supplier(lambda: self._get_entity_axissystem(bindname)))
    #TODO: add (unmodified) plugins for ("get_entity", "view", "local") and all other views
  def place(self):
    libcontext.socket("get_entity", socket_single_required(self.set_entityfunc))
    libcontext.socket(("get_entity", "NodePath"), socket_single_required(self.set_entityfunc_nodepath))
    libcontext.socket(("get_entity", "AxisSystem"), socket_single_required(self.set_entityfunc_axissystem))
    #TODO: add sockets for ("get_entity", "view", "local") and all other views

class entitybinder_view(binderdrone):
  def set_entityfunc(self, entityfunc):
    self._get_entity = entityfunc
  def set_entityfunc_nodepath(self, entityfunc_nodepath):
    self._get_entity_nodepath = entityfunc_nodepath    
  def set_entityfunc_axissystem(self, entityfunc_axissystem):
    self._get_entity_axissystem = entityfunc_axissystem        
  def bind(self, binderworker, bindname):
    libcontext.plugin("entity", plugin_supplier(lambda: self._get_entity(bindname)))
    libcontext.plugin(("entity","NodePath"), plugin_supplier(lambda: self._get_entity_nodepath(bindname)))
    libcontext.plugin(("entity","AxisSystem"), plugin_supplier(lambda: self._get_entity_axissystem(bindname)))
    #TODO: add (unmodified) plugins for ("get_entity", "view", self._view) and all other views
  def place(self):
    libcontext.socket(("get_entity", "view", self._view), socket_single_required(self.set_entityfunc))
    libcontext.socket(("get_entity", "view", self._view, "NodePath"), socket_single_required(self.set_entityfunc_nodepath))
    libcontext.socket(("get_entity", "view", self._view, "AxisSystem"), socket_single_required(self.set_entityfunc_axissystem))
    #TODO: add (unmodified) sockets for all other views than ("get_entity", "view", self._view) 

class entitybinder_local(entitybinder_view):
  _view = "local"

class entitybinder_relative(entitybinder_view):
  _view = "relative"
  
class entitycamerabinder(binderdrone):
  def bind(self, binderworker):
    #... 
    raise Exception("TODO")

class actorbinder(binderdrone):
  def set_actorfunc(self, actorfunc):
    self._get_actor = actorfunc
  def bind(self, binderworker, bindname):
    libcontext.plugin("actor", plugin_supplier(lambda: self._get_actor(bindname)))
  def place(self):
    libcontext.socket("get_actor", socket_single_required(self.set_actorfunc))
 
class actoroptionalbinder(binderdrone):
  def set_actorfunc(self, actorfunc):
    self._get_actor = actorfunc
  def bind(self, binderworker, bindname):
    try:
      self._get_actor(bindname) 
    except KeyError:
      pass
    else:
      libcontext.plugin("actor", plugin_supplier(lambda: self._get_actor(bindname)))
  def place(self):
    libcontext.socket("get_actor", socket_single_required(self.set_actorfunc))


class camerabinder(binderdrone):
  def bind(self, binderworker, bindname):
    libcontext.plugin("entity", plugin_supplier(self.camera))
  def set_camera(self, camera):
    self.camera = camera
  def place(self):
    libcontext.socket("camera", socket_single_required(self.set_camera))
        
class entitybridge(binderdrone):
  def bind(self, binderworker):
    #... 
    raise Exception("TODO")
    
class entityclassonlybridge(binderdrone):
  def bind(self, binderworker):
    #... 
    raise Exception("TODO")
    
class entityclear(binderdrone):
  def bind(self, binderworker):
    #... 
    raise Exception("TODO")

class bind(bind_baseclass):
  bind_entity = bindparameter(True)
  binder("bind_entity", False, None)
  binder("bind_entity", True, entitybinder(), "bindname") #the matrix of the entity
  binder("bind_entity", "local", entitybinder_local(), "bindname") 
  binder("bind_entity", "relative", entitybinder_relative(), "bindname")   
  binder("bind_entity", "camera", entitycamerabinder()) 
  bind_actor = bindparameter("optional")
  binder("bind_actor", False, None)
  binder("bind_actor", "optional", actoroptionalbinder(), "bindname")
  binder("bind_actor", True, actorbinder(), "bindname")
  bind_camera = bindparameter("transmit")
  binder("bind_camera", False, None)
  binder("bind_camera", "transmit", pluginbridge("camera")) 
  binder("bind_camera", "transmit", pluginbridge("get_camera")) 
  binder("bind_camera", "entity", camerabinder(), "bindname") 
  entitydata = bindparameter(None) #also for actors and entity/actorclasses!
  binder("entitydata", None, None)
  binder("entitydata", "transmit", entitybridge()) #also bridges spawning and classes
  binder("entitydata", "class-only", entityclassonlybridge()) #clears entitydict and actordict, but maintains the classes
  binder("entitydata", "clear", entityclear()) #clears entitydict and actordict and removes entityclasses and actorclasses
