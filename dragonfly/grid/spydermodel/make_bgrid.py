def make_bgrid(bg):
  from ..bgrid import bgrid
  values = []
  minx=bg.minx
  maxx=bg.maxx
  miny=bg.miny
  maxy=bg.maxy
  if bg.values is not None:
    values = [(v.x,v.y) for v in bg.values]
  else:
    if minx is None: minx = 0
    if maxx is None: maxx = 0
    if miny is None: miny = 0
    if maxy is None: maxy = 0
  return bgrid (
    minx=minx,
    maxx=maxx,
    miny=miny,
    maxy=maxy,
    values = values
  )
