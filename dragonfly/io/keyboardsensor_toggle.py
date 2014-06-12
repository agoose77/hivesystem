import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from ._inputsensor import keyboardsensor_base
from ..keycodes import *
import sys

python2 = (sys.version_info[0] == 2)


class keyboardsensor_toggle(keyboardsensor_base):
    keycode = variable("str")
    parameter(keycode, "SPACE")

    press = output("push", "trigger")
    trigger_pressed = triggerfunc(press)
    release = output("push", "trigger")
    trigger_released = triggerfunc(release)

    v_pressed = variable("bool")
    startvalue(v_pressed, False)
    pressed = output("pull", "bool")
    connect(v_pressed, pressed)

    def _trigger_pressed(self, event):
        # ignore event
        self.trigger_pressed()
        self.v_pressed = True

    def _trigger_released(self, event):
        # ignore event
        self.trigger_released()
        self.v_pressed = False

    def place(self):
        libcontext.socket(("evin", ("input", "keyboard", "keyreleased")), socket_flag())
        if self.keycode not in asciilist:
            libcontext.socket(("evin", ("input", "keyboard", "extended")), socket_flag())
        place = keyboardsensor_base.place
        if python2: place = place.im_func
        place(self)

    def enable(self):
        self.add_listener("leader", self._trigger_pressed, ("keyboard", "keypressed", self.keycode))
        self.add_listener("leader", self._trigger_released, ("keyboard", "keyreleased", self.keycode))

    def disable(self):
        self.remove_listener("leader", self._trigger_pressed, ("keyboard", "keypressed", self.keycode))
        self.remove_listener("leader", self._trigger_released, ("keyboard", "keyreleased", self.keycode))
