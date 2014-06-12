import spyder, Spyder
import characteraction
from Spyder import CharacterAction
import bee
class action2hive(bee.frame):
  d = bee.init("dictionary")
  d["run"] = CharacterAction (
   animation = "running.animation",
   soundfile = "run.wav",
  )
  #or: d["run"] = CharacterAction("running.animation", "run.wav")
  d["shoot"] = CharacterAction (
   animation = "shooting.animation",
   soundfile = "shoot.wav",
  )
  #or: d["shoot"] = CharacterAction("shooting.animation", "shoot.wav")
