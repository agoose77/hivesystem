from bee import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *


class movereporter(drone):
    def print_move(self, move):
        print(move)

    def place(self):
        p = plugin_supplier(self.print_move)
        libcontext.plugin(("game", "make_move"), p)
