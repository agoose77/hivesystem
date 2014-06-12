import somelibrary


class action1component(object):
    def __init__(self):
        adict = {}
        sdict = {}
        adict["walk"] = "walk-animation"
        sdict["walk"] = "walking.wav"

        adict["jump"] = "jump-animation"
        sdict["jump"] = "jmp.wav"
        self.animdict = adict
        self.sounddict = sdict

    def animplay(self, id_anim):
        anim = self.animdict[id_anim]
        somelibrary.play_animation(anim)

    def soundplay(self, id_sound):
        sound = self.sounddict[id_sound]
        somelibrary.play_sound(sound)
