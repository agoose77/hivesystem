import bee
class action3hive(bee.frame):
  init_animationmanager = bee.init("animationmanager")
  init_soundmanager = bee.init("soundmanager")
  
  init_animationmanager.add_animation("swim", "splash-animation")
  init_soundmanager.add_sound("swim", "splash.wav")

  init_animationmanager.add_animation("crouch", "crouching")
  init_soundmanager.add_sound("crouch", "crouch.wav")
