from CharacterAction import CharacterAction

import somelibrary


class action2component(object):
    def __init__(self):
        d = {}
        d["run"] = CharacterAction(
            animation="running.animation",
            soundfile="run.wav",
        )
        # or: d["run"] = CharacterAction("running.animation", "run.wav")

        d["shoot"] = CharacterAction(
            animation="shooting.animation",
            soundfile="shoot.wav",
        )
        #or: d["shoot"] = CharacterAction("shooting.animation", "shoot.wav")

        self.actiondict = d

    def actionplay(self, id_action):
        action = self.actiondict[id_action]
        somelibrary.play_animation(action.animation)
        somelibrary.play_sound(action.soundfile)
