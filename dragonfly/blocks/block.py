import bee
from bee.segments import *
import spyder, Spyder
import spyder.formtools
import libcontext

class block(object):
  metaguiparams = {"spydertype":"type"}
  def __new__(cls, spydertype):
    assert spyder.validvar2(spydertype), spydertype
    class block(bee.worker):
      value = variable(spydertype)
      parameter(value, None)
      
      block_ = output("pull", "block")
      v_block = variable("block")
      connect(v_block, block_)
      
      control = antenna_blockcontrol()

      model = output("pull", "blockmodel")
      v_model = variable("blockmodel")
      connect(v_model, model)
      
      def set_block(self, model):
        self.v_model = model
        self.v_block = model
        self.control.set_blockcontrol(lambda: self.v_model)
      
      def _init(self):
        spyderclass = getattr(Spyder, spydertype)
        model = spyder.formtools.model(spyderclass)
        if self.value is not None:
          model._set(self.value)       
        self.set_block(model)
                      
      def place(self):
        p = libcontext.pluginclasses.plugin_single_required(self._init)
        libcontext.plugin(("bee", "init"), p)
        
    return block
      
      
               
  
