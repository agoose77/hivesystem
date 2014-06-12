import spyder, Spyder
from .action3hive import action3hive
from Spyder import CharacterActionItem, CharacterAction
class action3conf(action3hive):
  attribute_1 = CharacterActionItem (
    identifier = 'swim',
    action = CharacterAction (
      animation = 'splash-animation',
      soundfile = 'splash.wav',
    ),
  )

  #or: 
  # attribute_1 = CharacterActionItem("swim", ("splash-animation", "splash.wav"))
  attribute_2 = CharacterActionItem (
    identifier = 'crouch',
    action = CharacterAction (
      animation = 'crouching',
      soundfile = 'crouch.wav',
    ),
  )
  #or: 
  # attribute_2 = CharacterActionItem("crouch", ("crouching", "crouch.wav"))

