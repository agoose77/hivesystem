import bee, libcontext

class hiveregister(bee.drone):
  def __init__(self):
    self.hives = {}  
  def register_hive(self, hivename, hive):
    self.hives[hivename] = hive
  def get_hive(self, hivename):
    return self.hives[hivename]
  def place(self):
    p = libcontext.pluginclasses.plugin_supplier(self.get_hive)
    libcontext.plugin("get_hive", p)
    
