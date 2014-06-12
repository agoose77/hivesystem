from bee import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from ..UCIChessEngine import UCIChessEngine


class chessUCI(drone):
    def __init__(self, player, engine_binary, engine_dir=None):
        assert player in ("White", "Black")
        self.player = player
        self.moveprocessors = []
        self.UCIengine = UCIChessEngine(engine_binary, engine_dir)

    def make_move(self, move):
        self.UCIengine.make_move(move)
        if self.player is not self.turn():
            self.event_next(("game", "engine", id(self.UCIengine), "get_move"))

    def add_moveprocessor(self, moveprocessor):
        self.moveprocessors.append(moveprocessor)

    def set_turn(self, turn_func):
        self.turn = turn_func

    def move(self):
        if self.turn() != self.player: raise ValueError
        move = self.UCIengine.get_move()
        for f in self.moveprocessors: f(move)

    def set_event_next(self, event_next):
        self.event_next = event_next

    def start(self):
        if self.player == "White":
            self.event_next(("game", "engine", id(self.UCIengine), "get_move"))

    def place(self):
        p = plugin_supplier(self.make_move)
        libcontext.plugin(("game", "make_move"), p)

        s = socket_single_required(self.set_turn)
        libcontext.socket(("game", "turn"), s)

        s = socket_container(self.add_moveprocessor)
        libcontext.socket(("game", "process_move"), s)

        s = socket_single_required(self.set_event_next)
        libcontext.socket(("evin", "event", "next"), s)

        listener = plugin_single_required(("match", self.move, ("game", "engine", id(self.UCIengine), "get_move")))
        libcontext.plugin(("evin", "listener"), listener)

        listener = plugin_single_required(("trigger", self.start, "start"))
        libcontext.plugin(("evin", "listener"), listener)
