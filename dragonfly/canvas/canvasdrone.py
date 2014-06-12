"""
what we have:
- show OR draw
- update, remove 
- reserved identifiers
What we need:
show1: obj; returns id
show2: obj, id
draw1: obj, bbox; returns id
draw2: obj, bbox, id
draw3: obj, id
update1: id       (draw or show)
update2: id, bbox (draw only)
update3: id, parameters (draw or show)

In addition:
boundingboxes
and get_boundingbox

identifier management (also "remove" plugin)
connect mouseareas with boundingboxes: remove/update must also effect areas! 
"""

class canvasargs(object):
  def __init__(self, *args, **kwargs):
    obj = None
    identifier = None
    box = None
    parameters = None
    
    assert len(args) <= 4
    
    if len(args): obj = args[0]
    else: obj = kwargs.get("obj", None)
    if len(args) > 1: identifier = args[0]
    else: identifier = kwargs.get("identifier", None)
    if len(args) > 2: box = args[2]
    elif "box" in kwargs: box = kwargs["box"]
    elif "bbox" in kwargs: box = kwargs["bbox"]
    if len(args) > 3: parameters = args[3]
    elif "parameters" in kwargs: box = kwargs["parameters"]
    elif "params" in kwargs: box = kwargs["params"]
    
    assert obj is not None #canvas object   
    self.obj = obj
    self.identifier = identifier
    self.box = box
    self.parameters = parameters

import bee, libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

import functools
expand_plugins = set(("draw", "draw0", "show", "show0", "remove", "update"))
class canvasdrone(bee.drone): 
  def __init__(self):
    self._canvasobjects = {}
    self._idcount = {}
    self._classname = self.__class__.__name__.rstrip("&")
    self._reserves = {}  
    self._placed = False  
    self._expandtypes = {}
    
    self._drawfuncs = {}
    self._showfuncs = {}
    self._updatefuncs = {}
    self._removefuncs = {}
    
    self._showdraw_inits = []
    self._has_mouseareas = False
    
  def _set_canvasobject(self, identifier, typ, obj, bbox, parameters):
    self._canvasobjects[identifier] = (typ, obj, bbox, parameters)
    if self._has_mouseareas:
      if identifier in self._mouseareas:
        self._mouseareas[identifier] = bbox
    
  def _get_identifier(self,idtype,idnr):
    return "%s-%s-%d" % (self._classname, idtype,idnr)
  def _get_new_idnr(self, idtype):  
    if idtype not in self._idcount: self._idcount[idtype] = 0
    self._idcount[idtype] += 1
    return self._idcount[idtype]

  def set_parent(self, parent):
    self.parent = parent

  def reserve(self, identifier, type_=None, box=None, parameters=None):
    if self._placed:
      raise Exception("canvasdrone.reserve must be called before place()")
    type_ = bee.resolve(type_, self.parent)
    box = bee.resolve(box, self.parent)
    parameters = bee.resolve(parameters, self.parent)
    self._reserves[identifier] = (type_, box, parameters)

  def dynamic_reserve(self, identifier, type_=None, box=None, parameters=None):
    self._set_canvasobject(identifier, type_, None, box, parameters)

  def _draw1(self, typ, obj, bbox, parameters = None):
    drawfunc = self._drawfuncs[typ]
    idnr = self._get_new_idnr(typ)
    identifier = self._get_identifier(typ, idnr)
    drawfunc(obj, identifier, bbox, parameters = parameters)
    self._set_canvasobject(identifier, typ, obj, bbox, parameters)
    return identifier
  def _draw2(self, typ, obj, bbox, identifier, parameters = None):
    if identifier in self._canvasobjects:
      updatefunc = self._updatefuncs[typ]
      curr = self._canvasobjects[identifier]
      if curr[0] is not None and curr[0] != typ:
        raise TypeError(
         "Canvas identifier '%s' has been registered for type '%s', attempted drawing with type '%s'" \
          % (identifier, curr[0], typ)
        )
      if parameters is None: 
        parameters = curr[3]
      updatefunc(obj, identifier, bbox, parameters = parameters)
    else:
      drawfunc = self._drawfuncs[typ]
      drawfunc(obj, identifier, bbox, parameters = parameters)
    self._set_canvasobject(identifier, typ, obj, bbox, parameters)
  def _draw3(self, typ, obj, identifier):
    updatefunc = self._updatefuncs[typ]
    curr = self._canvasobjects[identifier]
    if curr[0] is not None and curr[0] != typ:
      raise TypeError(
       "Canvas identifier '%s' has been registered for type '%s', attempted drawing with type '%s'" \
        % (identifier, curr[0], typ)
      )
    bbox, parameters = curr[2], curr[3]
    if curr[1] is None:
      drawfunc = self._drawfuncs[typ]
      drawfunc(obj, identifier, bbox, parameters = parameters)
    else:  
      updatefunc(obj, identifier, bbox, parameters = parameters)
    self._set_canvasobject(identifier, typ, obj, bbox, parameters)
  def _show1(self, typ, obj, parameters = None):
    showfunc = self._showfuncs[typ]
    idnr = self._get_new_idnr(typ)
    identifier = self._get_identifier(typ, idnr)
    showfunc(obj, identifier, parameters = parameters)
    bbox = None
    self._set_canvasobject(identifier, typ, obj, bbox, parameters)
    return identifier
  def _show2(self, typ, obj, identifier, parameters = None):
    if identifier in self._canvasobjects:
      updatefunc = self._updatefuncs[typ]
      curr = self._canvasobjects[identifier]
      if curr[0] != typ:
        raise TypeError(
         "Canvas identifier '%s' has been registered for type '%s', attempted drawing with type '%s'" \
          % (identifier, curr[0], typ)
        )
      if parameters is None: 
        parameters = curr[3]
      updatefunc(obj, identifier, parameters = parameters)
    else:
      showfunc = self._showfuncs[typ]
      showfunc(obj, identifier, parameters = parameters)
    bbox = None
    self._set_canvasobject(identifier, typ, obj, bbox, parameters)
  
  def _update1show(self, typ, identifier):    
    if identifier not in self._canvasobjects: return False
    updatefunc = self._updatefuncs[typ]
    curr = self._canvasobjects[identifier]
    obj, parameters = curr[1], curr[3]
    updatefunc(obj, identifier, parameters = parameters)
    return True
  def _update1draw(self, typ, identifier):    
    if identifier not in self._canvasobjects: return False
    updatefunc = self._updatefuncs[typ]
    curr = self._canvasobjects[identifier]
    obj, bbox, parameters = curr[1], curr[2], curr[3]
    updatefunc(obj, identifier, bbox, parameters = parameters)
    return True
  def _update1(self, identifier):
    if identifier not in self._canvasobjects: return False
    curr = self._canvasobjects[identifier]
    typ = curr[0]
    if self._expandtypes[typ] == "show":
      self._update1show(typ, identifier)
    else: #draw
      self._update1draw(typ, identifier)
    return True

  def _update2draw(self, typ, identifier, bbox):
    updatefunc = self._updatefuncs[typ]
    curr = self._canvasobjects[identifier]
    obj, parameters = curr[1], curr[3]
    updatefunc(obj, identifier, bbox, parameters = parameters)
    self._set_canvasobject(identifier, typ, obj, bbox, parameters)
  def _update2(self, identifier, bbox):
    if identifier not in self._canvasobjects: return False
    curr = self._canvasobjects[identifier]
    typ = curr[0]
    if self._expandtypes[typ] == "show":
      raise TypeError("Canvas type %s: bounding boxes are only supported for 'draw', not 'show'" % typ) 
    else: #draw
      self._update2draw(typ, identifier, bbox)
    return True

  def _update3show(self, typ, identifier, parameters):
    updatefunc = self._updatefuncs[typ]
    curr = self._canvasobjects[identifier]
    obj = curr[1]
    updatefunc(obj, identifier, parameters = parameters)
    self._set_canvasobject(identifier, typ, obj, bbox, parameters)
  def _update3draw(self, typ, identifier, parameters):
    updatefunc = self._updatefuncs[typ]
    curr = self._canvasobjects[identifier]
    obj, bbox = curr[1], curr[2]
    updatefunc(obj, identifier, bbox, parameters = parameters)
    self._set_canvasobject(identifier, typ, obj, bbox, parameters)
  def _update3(self, identifier, parameters):
    if identifier not in self._canvasobjects: return False
    curr = self._canvasobjects[identifier]
    typ = curr[0]
    if self._expandtypes[typ] == "show":
      self._update3show(typ, identifier, parameters)
    else: #draw
      self._update3draw(typ, identifier, parameters)
    return True

  def _remove(self, identifier):    
    if identifier not in self._canvasobjects: return False
    curr = self._canvasobjects[identifier]
    typ = curr[0]
    removefunc = self._removefuncs[typ]
    removefunc(identifier)
    self._canvasobjects.pop(identifier)
    return True
  
  def _set_drawfunc(self, typ, drawfunc):
    self._drawfuncs[typ] = drawfunc
  def _set_showfunc(self, typ, showfunc):
    self._showfuncs[typ] = showfunc
  def _set_updatefunc(self, typ, updatefunc):
    self._updatefuncs[typ] = updatefunc
  def _set_removefunc(self, typ, removefunc):
    self._removefuncs[typ] = removefunc
    
  def _add_showdraw_init(self, typ, args):
    assert isinstance(args, canvasargs)
    self._showdraw_inits.append((typ, args))    
  def _showdraw_init(self):
    for typ, args in self._showdraw_inits:
      showdraw = self._expandtypes[typ]
      obj = args.obj
      identifier = args.identifier
      if identifier is None:
        idnr = self._get_new_idnr(typ)
        identifier = self._get_identifier(typ, idnr)
      parameters = args.parameters
      box = args.box
      if showdraw == "show": 
        showfunc = self._showfuncs[typ]
        i = showfunc(obj, identifier, parameters = parameters)        
      else:
        assert box is not None #boundingbox
        drawfunc = self._drawfuncs[typ]
        i = drawfunc(obj, identifier, box, parameters = parameters)        
      if identifier is None: identifier = i

      self._set_canvasobject(identifier, typ, obj, box, parameters)

  def _set_mouseareas(self, mouseareas):
    self._has_mouseareas = True  
    self._mouseareas = mouseareas
    
  def place(self):    
    self._placed = True
    #process reserves
    for identifier in self._reserves:
      type_, bbox, parameters = self._reserves[identifier]
      p = plugin_supplier(type_, bbox, parameters)
      libcontext.plugin(("canvas","reserve", identifier), p)
    
    #expand plugins
    plugs = dict(libcontext.get_curr_context().plugins)
    plug_detect = {}
    for plug in plugs:
      if not isinstance(plug, tuple): continue      
      if len(plug) != 3: continue
      if plug[0] != "canvas": continue
      if plug[1] not in expand_plugins: continue
      typ = plug[2]
      if plug[2] not in plug_detect: plug_detect[typ] = set()
      plug_detect[typ].add(plug[1])
    for typ in plug_detect:
      p = plug_detect[typ]
      has_show = "show" in p
      has_draw = "draw" in p
      if has_show and has_draw in p:
        raise TypeError(
         "Canvasdrone: cannot expand 'show' AND 'draw' function plugins for %s, only one can exist" % typ
        )
      if not has_show and not has_draw:
        raise TypeError(
         "Canvasdrone: cannot expand plugins for %s: declares %s but neither 'show' nor 'draw'" % (typ, list(p))
        )
      if not "update" in p:
        raise TypeError(
         "Canvasdrone: cannot expand plugins for %s: declares %s but not 'update'" % (typ, list(p))
        )
      if not "remove" in p:
        raise TypeError(
         "Canvasdrone: cannot expand plugins for %s: declares %s but not 'remove'" % (typ, list(p))
        )
      
      if has_show:
        s = socket_container(functools.partial(self._add_showdraw_init, typ))
        libcontext.socket(("canvas", "show", "init", typ), s)      

        s = socket_single_required(functools.partial(self._set_showfunc, typ))
        libcontext.socket(("canvas", "show", typ), s)      
        p = plugin_supplier(functools.partial(self._show1, typ)) 
        libcontext.plugin(("canvas", "show1", typ), p)      
        p = plugin_supplier(functools.partial(self._show2, typ)) 
        libcontext.plugin(("canvas", "show2", typ), p)      
        
        self._expandtypes[typ] = "show"
      else: #has_draw
        s = socket_container(functools.partial(self._add_showdraw_init, typ))
        libcontext.socket(("canvas", "draw", "init", typ), s)      

        s = socket_single_required(functools.partial(self._set_drawfunc, typ))
        libcontext.socket(("canvas", "draw", typ), s)      
        p = plugin_supplier(functools.partial(self._draw1, typ)) 
        libcontext.plugin(("canvas", "draw1", typ), p)      
        p = plugin_supplier(functools.partial(self._draw2, typ)) 
        libcontext.plugin(("canvas", "draw2", typ), p)      
        p = plugin_supplier(functools.partial(self._draw3, typ)) 
        libcontext.plugin(("canvas", "draw3", typ), p)      
                
        self._expandtypes[typ] = "draw"

      s = socket_single_required(functools.partial(self._set_updatefunc, typ))        
      libcontext.socket(("canvas", "update", typ), s)      
      s = socket_single_required(functools.partial(self._set_removefunc, typ))
      libcontext.socket(("canvas", "remove", typ), s)
      
    p = plugin_supplier(self._remove)
    libcontext.plugin(("canvas", "remove1"), p)
    p = plugin_supplier(self.dynamic_reserve)
    libcontext.plugin(("canvas", "dynamic-reserve"), p)
    p = plugin_supplier(self._update1)
    libcontext.plugin(("canvas", "update1"), p)
    p = plugin_supplier(self._update2)
    libcontext.plugin(("canvas", "update2"), p)
    p = plugin_supplier(self._update3)
    libcontext.plugin(("canvas", "update3"), p)

    p = plugin_single_required(self._showdraw_init)
    libcontext.plugin(("bee", "init"), p)

    s = socket_single_optional(self._set_mouseareas)
    libcontext.socket(("canvas","mousearea","mouseareas"), s)
      
    #TODO: dragonfly.logic.set_attribute/get_attribute
