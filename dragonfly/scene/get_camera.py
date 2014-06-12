from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class get_camera(worker):
  camera_identifier = variable("id")
  camera = output("pull","id")
  connect(camera_identifier, camera)
  def init(self):
    self.camera_identifier = self.get_camera()
  def set_get_camera(self, get_camera):
    self.get_camera = get_camera
  def place(self):
    libcontext.socket("get_camera",socket_single_required(self.set_get_camera))
    libcontext.plugin("startupfunction",plugin_single_required(self.init))
