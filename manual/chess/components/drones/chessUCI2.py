import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from .chessUCI import chessUCI

import time


class chessUCI2(chessUCI):
    def move(self):
        chessUCI._wrapped_hive.move(self)
        time.sleep(1.0)

    def place(self):
        p = plugin_supplier(self.make_move)
        libcontext.plugin(("game", "make_move"), p)

        s = socket_single_required(self.set_turn)
        libcontext.socket(("game", "turn"), s)

        s = socket_container(self.add_moveprocessor)
        libcontext.socket(("game", "process_move"), s)

        s = socket_single_required(self.set_event_next)
        libcontext.socket(("evin", "event", "next_tick"), s)

        listener = plugin_single_required(("match", self.move, ("game", "engine", id(self.UCIengine), "get_move")))
        libcontext.plugin(("evin", "listener"), listener)

        listener = plugin_single_required(("trigger", self.start, "start"))
        libcontext.plugin(("evin", "listener"), listener)
