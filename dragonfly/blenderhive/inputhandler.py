import bee
from bee import event

import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

trans = {}


def init():
    import bge

    trans.clear()
    for key, value in bge.events.__dict__.items():
        if not key.endswith("KEY"):
            if key.startswith("PAD"):
                if len(key) == 4:
                    trans[value] = key[-1]
                elif key == "PADPERIOD":
                    trans[value] = "."
                elif key == "PADMINUS":
                    trans[value] = "-"
                elif key == "PADENTER":
                    trans[value] = "RETURN"
            else:
                continue
        key = key[:-3]
        if len(key) == 1:
            if ord(key) >= 65 and ord(key) < 65 + 26:
                trans[value] = key
        elif key[0] == "F" and key[1].isdigit():
            trans[value] = key
        elif key == "ZERO":
            trans[value] = "0"
        elif key == "ONE":
            trans[value] = "1"
        elif key == "TWO":
            trans[value] = "2"
        elif key == "THREE":
            trans[value] = "3"
        elif key == "FOUR":
            trans[value] = "4"
        elif key == "FIVE":
            trans[value] = "5"
        elif key == "SIX":
            trans[value] = "6"
        elif key == "SEVEN":
            trans[value] = "7"
        elif key == "EIGHT":
            trans[value] = "8"
        elif key == "NINE":
            trans[value] = "9"
        elif key.startswith("PAD"):
            if key == "PADSLASH":
                trans[value] = "/"
            elif key == "PADASTER":
                trans[value] = "*"
            elif key == "PADPLUS":
                trans[value] = "+"
        elif key == "ACCENTGRAVE":
            trans[value] = "`"
        elif key == "BACKSLASH":
            trans[value] = "\\"
        elif key == "COMMA":
            trans[value] = ","
        elif key == "DEL":
            trans[value] = "DELETE"
        elif key == "END":
            trans[value] = "DELETE"
        elif key == "EQUAL":
            trans[value] = "="
        elif key == "ESC":
            trans[value] = "ESCAPE"
        elif key == "HOME":
            trans[value] = "HOME"
        elif key == "INSERT":
            trans[value] = "INSERT"
        elif key == "LEFTBRACKET":
            trans[value] = "["
        # LINEFEEDKEY?
        elif key == "RIGHTBRACKET":
            trans[value] = "]"
        elif key == "MINUS":
            trans[value] = "-"
        elif key == "PAGEDOWN":
            trans[value] = "PAGEDOWN"
        elif key == "PAGEUP":
            trans[value] = "PAGEUP"
        elif key == "PAUSE":
            trans[value] = "PAUSE"
        elif key == "PERIOD":
            trans[value] = "."
        elif key == "QUOTE":
            trans[value] = "'"
        elif key == "ENTER":
            trans[value] = "RETURN"
        elif key == "SEMICOLON":
            trans[value] = ";"
        elif key == "SLASH":
            trans[value] = "/"
        elif key == "SPACE":
            trans[value] = "SPACE"
        elif key == "TAB":
            trans[value] = "TAB"


        #TODO: modifiers?
        elif key.endswith("ARROW"):
            trans[value] = key[:-len("ARROW")]


class inputhandler(bee.drone):
    def __init__(self):
        self.targets = []
        self.just_pressed = set()
        self.just_released = set()

    def add_target(self, target):
        self.targets.append(target)

    def send_input(self):
        import bge

        keys = bge.logic.keyboard.events
        pressed = [k for k in keys if keys[k] == bge.logic.KX_INPUT_JUST_ACTIVATED]
        for key in pressed:
            if key not in trans: continue
            if key in self.just_pressed: continue
            self.just_pressed.add(key)
            if key in self.just_released: self.just_released.remove(key)
            e = event("keyboard", "keypressed", trans[key])
            for t in self.targets: t.add_event(e)
        released = [k for k in keys if keys[k] == bge.logic.KX_INPUT_JUST_RELEASED]
        for key in released:
            if key not in trans: continue
            if key in self.just_released: continue
            self.just_released.add(key)
            if key in self.just_pressed: self.just_pressed.remove(key)
            e = event("keyboard", "keyreleased", trans[key])
            for t in self.targets: t.add_event(e)

        buttons = bge.logic.mouse.events
        but = {
            "LEFT": buttons[bge.logic.KX_MOUSE_BUT_LEFT],
            "MIDDLE": buttons[bge.logic.KX_MOUSE_BUT_MIDDLE],
            "RIGHT": buttons[bge.logic.KX_MOUSE_BUT_RIGHT]
        }
        for button in but:
            v = but[button]
            if v == bge.logic.KX_INPUT_JUST_ACTIVATED:
                if button in self.just_pressed: continue
                self.just_pressed.add(button)
                if button in self.just_released: self.just_released.remove(button)
                e = event("mouse", "buttonpressed", button, self.get_mouse())
                for t in self.targets: t.add_event(e)
            elif v == bge.logic.KX_INPUT_JUST_RELEASED:
                if button in self.just_released: continue
                self.just_released.add(button)
                if button in self.just_pressed: self.just_pressed.remove(button)
                e = event("mouse", "buttonreleased", button, self.get_mouse())
                for t in self.targets: t.add_event(e)

    def get_mouse(self):
        import bge

        x, y = bge.logic.mouse.position
        return x, y

    def place(self):
        init()
        listener = plugin_single_required(("trigger", self.send_input, "send_input"))
        libcontext.plugin(("evin", "listener"), listener)

        libcontext.socket(("evout", "scheduler"), socket_container(self.add_target))
        libcontext.plugin(("evout", ("input", "keyboard")), plugin_flag())
        libcontext.plugin(("evout", ("input", "keyboard", "extended")), plugin_flag())
        libcontext.plugin(("evout", ("input", "keyboard", "keyreleased")), plugin_flag())
        libcontext.plugin(("evout", ("input", "mouse")), plugin_flag())

        libcontext.plugin(("evout", ("input", "get_mouse")), plugin_supplier(self.get_mouse))
