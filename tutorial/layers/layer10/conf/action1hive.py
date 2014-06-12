import bee


class action1hive(bee.frame):
    adict = bee.init("animdict")
    sdict = bee.init("sounddict")

    adict["walk"] = "walk-animation"
    sdict["walk"] = "walking.wav"

    adict["jump"] = "jump-animation"
    sdict["jump"] = "jmp.wav"

