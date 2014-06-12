class action3component(object):
  def __init__(self):
    self._initialized = False
    
  def set_animplayfunc(self, animplayfunc):
    self._animplay = animplayfunc
  def set_soundplayfunc(self, soundplayfunc):
    self._soundplay = soundplayfunc
  def set_addanimfunc(self, addanimfunc):
    self.add_animation = addanimfunc
  def set_addsoundfunc(self, addsoundfunc):
    self.add_sound = addsoundfunc
            
  def _init(self):
    if self._initialized: return
    self.add_animation("swim", "splash-animation")
    self.add_sound("swim", "splash.wav")
    self.add_animation("crouch", "crouching")
    self.add_sound("crouch", "crouch.wav")  
    self._initialized = True
    
  def animplay(self, anim):
    self._init()
    self._animplay(anim)
  def soundplay(self, sound):
    self._init()
    self._soundplay(sound)
    
