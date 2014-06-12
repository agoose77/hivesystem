from .worker import *

class bindworkerframe(workerframe):
  __filtered_segmentnames__ = ["bindworkerhive"]
  def build(self, hivename):
    ret = workerframe.build(self, hivename)
    self.bee.hive = self.hive
    return ret

class bindworkerwrapper(beewrapper):
  def __init__(self, *args, **kargs):
    self.args = args
    self.kargs = kargs
    self.kargs2 = kargs.copy()
    self.instance = None
    self.combobees = []
    self.combined = False
    if self.bindworkerhive is None:
      self.hive = None
    else:
      class bindworkerhive(self.bindworkerhive):
        pass
      self.hive = bindworkerhive
  def getinstance(self,__parent__=None):
    ret = beewrapper.getinstance(self,__parent__)    
    bindworkerinstancehive = None
    if self.hive != None:
      class bindworkerinstancehive(self.hive):
        pass
    self.instance.hive = bindworkerinstancehive
    return ret
  

class bindworkerbuilder(workerbuilder):
  __workerframeclass__ = bindworkerframe
  __workerwrapperclass__ = bindworkerwrapper
  
import sys
python3 = (sys.version_info[0] == 3)
if python3:
  e = """
class bindworker(worker,emptyclass,metaclass=bindworkerbuilder):
  pass
"""
  exec(e)  
else:
  class bindworker(worker,emptyclass):
    __metaclass__= bindworkerbuilder
