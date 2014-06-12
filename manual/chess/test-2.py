from components.UCIChessEngine import UCIChessEngine
from components.chesskeeper import chesskeeper

keeper = chesskeeper()
keeper.new()

u = UCIChessEngine("glaurung")
while not keeper.finished:
    move = u.get_move()
    fmove = keeper.format_move(move)
    print
    fmove
    keeper.make_move(fmove)
    u.make_move(fmove)
  
