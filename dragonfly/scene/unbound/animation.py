from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class animation(worker):
    start = Antenna("push", "trigger")
    stop = Antenna("push", "trigger")
    loop = Antenna("push", "trigger")
    actor = Antenna("pull", "id")
    b_actor = buffer("pull", "id")
    connect(actor, b_actor)
    animation_name = Antenna("pull", "str")
    v_animation_name = variable("str")
    t_animation_name = transistor("str")
    connect(animation_name, t_animation_name)
    connect(t_animation_name, v_animation_name)
    running = variable("bool")
    startvalue(running, False)

    @modifier
    def m_start(self):
        self.actor(self.b_actor).animate(self.v_animation_name)
        self.running = True

    trigger(start, b_actor)
    trigger(start, t_animation_name)
    trigger(start, m_start)

    @modifier
    def m_loop(self):
        self.actor(self.b_actor).animate(self.v_animation_name, loop=True)
        self.running = True

    trigger(loop, b_actor)
    trigger(loop, t_animation_name)
    trigger(loop, m_loop)

    @modifier
    def m_stop(self):
        if self.running:
            self.actor(self.b_actor).stop()
            self.running = False

    trigger(stop, b_actor)
    trigger(stop, m_stop)

    def set_actor(self, actor):
        self.actor = actor

    def place(self):
        libcontext.socket("get_actor", socket_single_required(self.set_actor))
    
