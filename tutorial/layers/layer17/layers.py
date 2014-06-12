from __future__ import print_function

# import the main and action components
from maincomponent import maincomponent
from action1 import action1component
from action2 import action2component
from action3 import action3component

#import manager components
from action3components import animationmanager
from action3components import soundmanager

#keyboard mainloop
from keycodes import ascii_to_keycode
from getch import getch, kbhit, change_termios, restore_termios


def mainloop(keyfunc=None):
    change_termios()
    while True:
        while not kbhit(): continue
        key = getch()
        if isinstance(key, bytes) and bytes != str: key = key.decode()
        if key not in ascii_to_keycode: continue
        keycode = ascii_to_keycode[key]
        if keycode == "ESCAPE": break
        if keyfunc is not None: keyfunc(keycode)
    restore_termios()

#define a generic pseudo-hive class    
import libcontext


class pseudohive(object):
    components = {}

    def __init__(self):
        for componentname, componentclass in self.components.items():
            component = componentclass()
            setattr(self, componentname, component)

    def build(self, contextname):
        self._contextname = contextname
        self._context = libcontext.context(self._contextname)

    def place(self):
        libcontext.push(self._contextname)
        for componentname, componentclass in self.components.items():
            component = getattr(self, componentname)
            component.place()
        libcontext.pop()

    def close(self):
        self._context.close()


#define the main (pseudo-)hive
class mainhive(pseudohive):
    components = {

        #action3 manager components
        "animationmanager": animationmanager,
        "soundmanager": soundmanager,

        #main component and action components
        "maincomponent": maincomponent,
        "action1": action1component,
        "action2": action2component,
        "action3": action3component,
    }

#Set up the main hive and run it

#Give us a new mainhive instance
main = mainhive()

#Build a context named "main"
main.build("main")

#Declare sockets and plugins
main.place()

#Build all connections, and validate the connection network
main.close()

#Run the main loop
main.maincomponent.start()
mainloop(main.maincomponent.keypress)
