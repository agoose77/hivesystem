"""
Interpolation can be started and stopped with triggers
When started, it pulls a fraction input every tick.
It then sends an interpolation between v_start and v_end based on this input

If it reaches the end (fraction==1), it sends a reach_end trigger instead of an interpolation
If it reaches the start (fraction==0), it sends a reach_start trigger instead of an interpolation

When fire_v_start is pushed, it sends v_start
When fire_v_end is pushed, it sends v_end
"""
import bee
from bee.segments import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

def interpolate(start, end, fraction):
  return start + fraction * (end - start)

class interpolation(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    class interpolation(bee.worker):
      v_running = variable("bool")
      startvalue(v_running, False)
      v_inp_old = None
      v_start = variable(type)
      parameter(v_start)      
      v_end = variable(type)
      parameter(v_end)
      
      inp = antenna("pull", ("float","fraction"))
      v_inp = buffer("pull",("float","fraction"))
      connect(inp, v_inp)
      outp = output("push", type)      
      w = weaver((type, type, ("float","fraction")), v_start, v_end, v_inp)
      op = operator(interpolate,(type, type, ("float","fraction")), type)
      t_op = transistor((type, type, ("float","fraction")))
      connect(w, t_op)
      connect(t_op, op)
      v_outp = variable(type)
      connect(op, v_outp)
      t_fire = transistor(type)
      connect(v_outp, t_fire)
      connect(t_fire, outp)

      #set fire True
      fire = variable("bool")
      @modifier
      def set_fire_true(self):
        self.fire = True

      #reach start / end

      reach_start = output("push", "trigger")
      trigger_reach_start = triggerfunc(reach_start)
      reach_end = output("push", "trigger")
      trigger_reach_end  = triggerfunc(reach_end)
      nochange = output("push", "trigger")
      trigger_nochange  = triggerfunc(nochange)
      
      #test zero / one / same
      @modifier
      def test_zero(self):
        if self.v_inp == 0:          
          self.fire = False
          self.trigger_reach_start()

      @modifier
      def test_one(self):
        if self.v_inp == 1:
          self.fire = False
          self.trigger_reach_end()          

      @modifier
      def test_same(self):
        if self.v_inp == self.v_inp_old:
          self.trigger_nochange()
        self.v_inp_old = self.v_inp

      tr_test_fire = transistor("bool")
      connect(fire, tr_test_fire)
      test_fire = test(tr_test_fire)
      trigger(test_fire, t_fire)
        
      trigger(v_outp, set_fire_true)
      trigger(v_outp, test_zero)
      trigger(v_outp, test_one)
      trigger(v_outp, test_same)
      trigger(v_outp, tr_test_fire)

      ## Fire v_start / v_end
      fire_v_start = antenna("push", "trigger")
      t_v_start = transistor(type)
      connect(v_start, t_v_start)
      connect(t_v_start, outp)
      trigger(fire_v_start, t_v_start)
      
      fire_v_end =  antenna("push", "trigger")
      t_v_end = transistor(type)
      connect(v_end, t_v_end)
      connect(t_v_end, outp)
      trigger(fire_v_end, t_v_end)
      
      ### Start and stop
      trig_v_inp = triggerfunc(v_inp)
      trig_op = triggerfunc(t_op)
      
      
      start = antenna("push", "trigger")
      @modifier
      def m_start(self):
        if not self.v_running:
          self.listener = self.add_listener("trigger", self.trig_v_inp, "tick", priority=1)
          self.listener2 = self.add_listener("trigger", self.trig_op, "tick", priority=1)
        self.v_running = True
      trigger(start, m_start)
      
      stop = antenna("push", "trigger")
      @modifier
      def m_stop(self):
        if self.v_running:
          self.remove_listener(self.listener)
          self.remove_listener(self.listener2)
        self.v_running = False
      trigger(stop, m_stop)

      def set_add_listener(self, add_listener):
        self.add_listener = add_listener
    
      def set_remove_listener(self, remove_listener):
        self.remove_listener = remove_listener
    
      def place(self):
        libcontext.socket(("evin","add_listener"), socket_single_required(self.set_add_listener))
        libcontext.socket(("evin","remove_listener"), socket_single_required(self.set_remove_listener))

    return interpolation
