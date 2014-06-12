import bee
from bee.segments import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *


class chessprocessor2(bee.worker):
    v_turn = variable("str")
    startvalue(v_turn, "White")
    turn = output("pull", "str")
    connect(v_turn, turn)

    inp_gamekeeper = antenna("pull", ("object", "gamekeeper"))
    gamekeeper = buffer("pull", ("object", "gamekeeper"))
    connect(inp_gamekeeper, gamekeeper)
    trig_gamekeeper = triggerfunc(gamekeeper)

    finished = output("push", "trigger")
    trig_finished = triggerfunc(finished)

    inp_move = antenna("push", ("str", "chess"))
    v_move = variable(("str", "chess"))
    connect(inp_move, v_move)

    outp_move = output("push", ("str", "chess"))
    v_outp_move = variable(("str", "chess"))
    t_outp_move = transistor(("str", "chess"))
    connect(v_outp_move, t_outp_move)
    connect(t_outp_move, outp_move)
    trig_outp_move = triggerfunc(t_outp_move)

    made_move = output("push", "trigger")
    trig_made_move = triggerfunc(made_move)

    @modifier
    def process_move(self):
        self.trig_gamekeeper()
        raiser_old = self.raiser_active()
        self.raiser_deactivate()
        try:
            move = self.gamekeeper.format_move(self.v_move)
            self.v_outp_move = move
            self.trig_outp_move()
        except ValueError:
            if raiser_old: self.raiser_activate()
            raise ValueError(self.v_move)
        except:
            if raiser_old: self.raiser_activate()
            raise

        if raiser_old: self.raiser_activate()
        if self.gamekeeper.finished: self.trig_finished()
        if self.v_turn == "White":
            self.v_turn = "Black"
        else:
            self.v_turn = "White"
        self.trig_made_move()

    trigger(v_move, process_move)

    def set_raiser_active(self, raiser_active):
        self.raiser_active = raiser_active

    def set_raiser_activate(self, raiser_activate):
        self.raiser_activate = raiser_activate

    def set_raiser_deactivate(self, raiser_deactivate):
        self.raiser_deactivate = raiser_deactivate

    def place(self):
        libcontext.socket(("eventhandler", "raiser", "active"),
                          socket_single_required(self.set_raiser_active))
        libcontext.socket(("eventhandler", "raiser", "activate"),
                          socket_single_required(self.set_raiser_activate))
        libcontext.socket(("eventhandler", "raiser", "deactivate"),
                          socket_single_required(self.set_raiser_deactivate))
  
  
