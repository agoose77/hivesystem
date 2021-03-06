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

#define the main class    
import libcontext


class mainclass(object):
    def __init__(self, contextname):
        self._contextname = contextname
        self._context = libcontext.context(self._contextname)

        #action3 manager components
        self.animationmanager = animationmanager()
        self.soundmanager = soundmanager()

        #main component and action components
        self.maincomponent = maincomponent()
        self.action1 = action1component()
        self.action2 = action2component()
        self.action3 = action3component()

    def place(self):
        libcontext.push(self._contextname)
        self.animationmanager.place()
        self.soundmanager.place()
        self.maincomponent.place()
        self.action1.place()
        self.action2.place()
        self.action3.place()
        libcontext.pop()

    def close(self):
        self._context.close()

    def run(self):
        self.maincomponent.start()
        mainloop(self.maincomponent.keypress)

#Set up the main class and run it

#Give us a new mainclass instance named "main"
main = mainclass("main")

#Declare sockets and plugins
main.place()

#Build all connections, and validate the connection network
main.close()

#Run the main loop
main.run()
