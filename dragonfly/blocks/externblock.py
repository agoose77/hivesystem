import bee
from bee.segments import *
import spyder, Spyder
import spyder.formtools
import libcontext


class externblock(object):
    metaguiparams = {"spydertype": "type"}

    def __new__(cls, spydertype):
        assert spyder.validvar2(spydertype), spydertype

        class externblock(bee.worker):
            block_ = antenna("pull", "block")
            b_block = buffer("pull", "block")
            connect(block_, b_block)
            get_block = triggerfunc(b_block)

            control = antenna_blockcontrol()

            model = output("pull", "blockmodel")
            v_model = variable("blockmodel")
            connect(v_model, model)

            @modifier
            def _init(self):
                if self._initialized: return
                self.get_block()
                model = self.b_block
                self.v_model = model
                self._initialized = True

            def place(self):
                self._initialized = False
                self.control.set_blockcontrol(lambda: self.v_model)

            pretrigger(v_model, _init)

        return externblock
      
      
               
  
