from bee import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from .. import chesskeeper as comp_chesskeeper


class chesskeeper(drone):
    def __init__(self):
        self.keeper = comp_chesskeeper.chesskeeper().new()

    def place(self):
        p = plugin_supplier(lambda: getattr(self.keeper, "finished"))
        libcontext.plugin(("game", "finished"), p)

        p = plugin_supplier(self.keeper.format_move)
        libcontext.plugin(("game", "format_move"), p)

        p = plugin_supplier(self.keeper.make_move)
        libcontext.plugin(("game", "make_move"), p)
    
    
  
