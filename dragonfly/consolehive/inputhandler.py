import threading, libcontext, bee
from .getch import *
from ..keycodes import *
from libcontext.pluginclasses import *
from libcontext.socketclasses import *
from bee import event


class inputhandler(bee.drone):
    def __init__(self):
        self.targets = []
        self.dead = None

    def add_target(self, target):
        self.targets.append(target)

    def process_key(self, key):
        if key not in ascii_to_keycode: return
        keycode = ascii_to_keycode[key]
        e = event("keyboard", "keypressed", keycode)
        for t in self.targets: t.add_event(e)

    def startup(self):
        def gkey(event, keyfunc):
            while not event.is_set():
                if not kbhit():
                    continue
                key = getch()
                if isinstance(key, bytes) and bytes != str: key = key.decode()
                keyfunc(key)

        change_termios()
        self.dead = threading.Event()
        t = threading.Thread(target=gkey, args=(self.dead, self.process_key,))
        t.daemon = True
        t.start()

    def restore_terminal(self):
        if self.dead is not None:
            self.dead.set()
        restore_termios()

    def place(self):
        libcontext.socket(("evout", "scheduler"), socket_container(self.add_target))
        libcontext.plugin(("evout", ("input", "keyboard")), plugin_flag())
        libcontext.plugin(("evout", ("input", "keyboard", "extended")), plugin_flag())
        libcontext.plugin("startupfunction", plugin_single_required(self.startup))
        libcontext.plugin("cleanupfunction", plugin_single_required(self.restore_terminal))
    
