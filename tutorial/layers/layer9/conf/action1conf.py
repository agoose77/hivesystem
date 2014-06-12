import spyder, Spyder
from .action1hive import action1hive
import characteraction
from Spyder import CharacterActionItem, CharacterAction
class action1conf(action1hive):
  attribute_1 = CharacterActionItem(
   identifier = "walk",
   action = CharacterAction (
    animation = "walk-animation",
    soundfile = "walking.wav",
   ), 
  )
  #or: 
  # attribute_1 = CharacterActionItem("walk", ("walk-animation", "walking.wav"))
  attribute_2 = CharacterActionItem(
   identifier = "jump",
   action = CharacterAction (
    animation = "jump-animation",
    soundfile = "jmp.wav",
   ), 
  )
  #or: 
  # attribute_2 = CharacterActionItem("jump", ("jump-animation", "jmp.wav"))

