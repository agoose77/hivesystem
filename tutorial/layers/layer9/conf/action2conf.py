import spyder, Spyder
from bee.spyderhive import spyderdicthive
import characteraction
from Spyder import CharacterAction
class action2conf(spyderdicthive):
  run = CharacterAction (
   animation = "running.animation",
   soundfile = "run.wav",
  )
  #or: run = CharacterAction("running.animation", "run.wav")
  shoot = CharacterAction (
   animation = "shooting.animation",
   soundfile = "shoot.wav",
  )
  #or: shoot = CharacterAction("shooting.animation", "shoot.wav")
