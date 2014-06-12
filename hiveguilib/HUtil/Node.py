from .Attribute import Attribute, Hook
from ..params import typetuple

basictypes = (
  "str", "String", 
  "int", "Integer",
  "float", "Float",
  "bool", "Bool",
)  

#Colors taken from Coral
colors = [
 (255,255,95),
 (255,0,0),
 (0,255,0),
 (204,255,102),
 (55,55,255),    
 (5,207,146),
 (255,160,130),
 (0,120,155),
 (0,120,155),
 (88,228,255),
 (255,255,255),
]

def map_type(type_):  
  t = type_
  if isinstance(t, tuple): 
    if typetuple(t):
      t = "object"
    else:
      t = t[0]

  if t == "object": 
    ret = colors[0]
  elif t == "trigger":
    ret = colors[1]
  elif t == "id":
    ret = colors[2]
  elif t in ("str", "String"):
    ret = colors[3]
  elif t in ("int", "Integer"):
    ret = colors[4]
  elif t in ("float", "Float"):
    ret = colors[5]
  elif t in ("bool", "Bool"):
    ret = colors[6]
  elif t in ("Coordinate", "Vector"):
    ret = colors[7]
  elif t == "AxisSystem":
    ret = colors[8]
  elif t == "Color":
    ret = colors[9]
  else: 
    ret = colors[10]
  return ret

class Node(object):
  def __init__(self, name, position, attributes, tooltip):
    self.name = name
    self.position = position
    self.attributes = attributes
    for a in attributes: assert isinstance(a, Attribute)
    self.tooltip = tooltip
  def get_attribute(self, attribute):
    at = [a for a in self.attributes if a.name == attribute]
    if len(at) == 0: 
      raise NameError("Node '%s' has no attribute named '%s'" % (self.name, attribute))
    elif len(at) > 1: 
      raise NameError("Node '%s' has %d attributes named '%s'" % (self.name, len(at), attribute))
    return at[0]      

 
def h_map_hook(hook, antenna):
  if hook is None: return None
  if hook.mode == "push": 
    shape = "circle"
    style = "solid"
  elif hook.mode == "pull":
    shape = "square"
    style = "dashed"
  else: #should not happen for hive system
    shape = "circle"
    style = "dot"
  color = map_type(hook.type)
  hover_text = "(%s,%s)" % (hook.mode, str(hook.type))
  order_dependent = False
  if not antenna and hook.mode == "push":
    order_dependent = True
  ret = Hook (
    shape,
    style,
    color,
    tooltip = hook.tooltip,
    visible = hook.visible,    
    hover_text = hover_text,
    order_dependent = order_dependent    
  )
  return ret
  
def h_map_attrib(attribute):
  inhook = h_map_hook(attribute.inhook, True)
  outhook = h_map_hook(attribute.outhook, False)
  value_on_newline = True
  if attribute.type in basictypes:
    value_on_newline = False
  
  ret = Attribute (
   attribute.name,
   inhook,
   outhook,
   attribute.label,
   attribute.value,
   value_on_newline,
   attribute.tooltip,
   attribute.visible
  )  
  return ret

def h_map_node(node):
  attribs = None
  if node.attributes is not None:
    attribs = [h_map_attrib(a) for a in node.attributes]
  ret = Node (
    node.name,
    node.position,
    attribs,
    node.tooltip
  )
  return ret
