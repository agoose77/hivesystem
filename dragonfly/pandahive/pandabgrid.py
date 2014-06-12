try:
  from panda3d.core import GeomVertexFormat, GeomVertexData
  from panda3d.core import Geom, GeomTristrips, GeomLines, GeomVertexWriter, GeomNode
  from panda3d.core import NodePath
  from panda3d.core import CardMaker
  import panda3d
except ImportError:
  panda3d = None
  
class pandabgrid(object):
  def __init__(self, canvasdrone, grid, identifier, parentnode, parameters):
    if panda3d is None: raise ImportError("Cannot locate Panda3D")
    self.grid = grid    
    self.identifier = identifier
    self.parentnode = parentnode
    self.parameters = parameters
    self._build_grid()
    self._update_grid()
  def update(self, grid, identifier, parentnode, parameters):
    self.grid = grid    
    self.identifier = identifier
    self.parameters = parameters
    self._update_grid()
    if parentnode is not self.parentnode:
      self.node.reparentTo(parentnode)
      self.parentnode = parentnode    
  def remove(self):
    pass
    
  def _update_grid(self):
    sx = self.grid.maxx-self.grid.minx+1
    sy = self.grid.maxy-self.grid.miny+1  
    if sx != self.sx or sy != self.sy:
      self.squares = None
      self.node.removeNode()
      self._build_grid()  
    for n in range(sx):
      for nn in range(sy):
        try:
          v = self.grid.get_value(self.grid.minx+n,self.grid.miny+nn)
        except ValueError:
          v = False
        square = self.squares[n,nn]
        if v == True:
          square.setColor(1,1,1,1)
        else:
          square.setColor(0,0,0,1)        

  def _build_grid(self):
    color = getattr(self.parameters, "color", (0,0,0,0))    

    node = NodePath(self.identifier)
    sx = self.grid.maxx-self.grid.minx+1
    sy = self.grid.maxy-self.grid.miny+1
        
    #1. the squares
    squares = {}
    card = CardMaker('')
    cardgeom = NodePath(card.generate())
    for n in range(sx):
      for nn in range(sy):
        square = NodePath(self.identifier+'-square-%d-%d' % (n+1,nn+1))
        cardgeom.instanceTo(square)
        square.setPos(float(n)/sx,0,-float(nn+1)/sy)
        square.setScale(1.0/sx,1,1.0/sy)
        square.setColor(0,0,0,1)
        square.reparentTo(node)
        squares[n,nn] = square    

    #2: the lines
    gnode = GeomNode(self.identifier+"-lines")    
    vformat = GeomVertexFormat.getV3cp()    
    vdata = GeomVertexData(self.identifier+'-lines', vformat, Geom.UHStatic)
    v_vertex = GeomVertexWriter(vdata, 'vertex')
    v_colors = GeomVertexWriter(vdata, 'color')
    
    for n in range(sx+1):  
      px = float(n)/sx
      v_vertex.addData3f(px,0.0,0.0)
      v_colors.addData4f(*color)
      v_vertex.addData3f(px,0,-1)
      v_colors.addData4f(*color)
    for n in range(sy+1):    
      py = float(n)/sy
      v_vertex.addData3f(0.0,0.0,-py)
      v_colors.addData4f(*color)
      v_vertex.addData3f(1.0,0,-py)
      v_colors.addData4f(*color)
    
    geom = Geom(vdata)    
    prim = GeomLines(Geom.UHStatic)
    for n in range(sx+1):
      prim.addVertex(2*n)
      prim.addVertex(2*n+1)
    for n in range(sy+1):
      prim.addVertex(2*(sx+n+1))
      prim.addVertex(2*(sx+n+1)+1)
      
    prim.closePrimitive()   
    geom.addPrimitive(prim)
    
    gnode.addGeom(geom)
    node1 = NodePath(gnode)
    node1.reparentTo(node)

    self.node, self.squares, self.sx, self.sy = node, squares, sx, sy
    self.node.reparentTo(self.parentnode)
