import bee
from bee.segments import *

class jumpworker2(bee.worker):
  height = variable("float")
  parameter(height)  
  position = variable("float")
  startvalue(position, 0)

  progress = antenna("pull", ("float","fraction"))
  v_progress = buffer("pull",("float","fraction"))
  connect(progress, v_progress)

  position = output("pull", "float")
  v_position = variable("float")
  connect(v_position, position)
 
  @modifier
  def jump(self):
    progress = self.v_progress
    avgvelocity = 4 * self.height * (1 - progress)
    self.v_position = progress * avgvelocity  
  pretrigger(v_position, v_progress, "output")
  pretrigger(v_position, jump, "output")
