from bee import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from .. import chessboard as comp_chessboard


class pandachessboard(comp_chessboard.chessboard):
    def __init__(self, boardparent):
        self.boardparent = boardparent
        comp_chessboard.chessboard.__init__(self)

    def move(self, move):
        self.boardparent.move(move)


class chessboard(drone):
    def __init__(self, player="Both"):
        assert player in ("White", "Black", "Both", None)
        self.player = player
        self.moveprocessors = []
        self.board = pandachessboard(self)

    def make_move(self, move):
        self.board.make_move(move)

    def add_moveprocessor(self, moveprocessor):
        self.moveprocessors.append(moveprocessor)

    def set_turn(self, turn_func):
        self.turn = turn_func

    def move(self, move):
        if self.player != "Both":
            if self.turn() != self.player or self.player is None: raise ValueError
        self.eventhandler_lock()
        try:
            for f in self.moveprocessors: f(move)
        finally:
            self.eventhandler_unlock()

    def set_eventhandler_lock(self, eventhandler_lock):
        self.eventhandler_lock = eventhandler_lock

    def set_eventhandler_unlock(self, eventhandler_unlock):
        self.eventhandler_unlock = eventhandler_unlock

    def place(self):
        p = plugin_supplier(self.make_move)
        libcontext.plugin(("game", "make_move"), p)

        s = socket_single_required(self.set_turn)
        libcontext.socket(("game", "turn"), s)

        s = socket_container(self.add_moveprocessor)
        libcontext.socket(("game", "process_move"), s)

        libcontext.socket(("eventhandler", "lock"),
                          socket_single_required(self.set_eventhandler_lock))

        libcontext.socket(("eventhandler", "unlock"),
                          socket_single_required(self.set_eventhandler_unlock))
    
