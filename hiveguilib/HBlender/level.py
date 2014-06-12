advanced_sparta = (
  #("sensors", "keyboard"),
  #("sensors", "mouse"),
  #("sensors", "collision"),
  #("sensors", "near"),
  #("sensors", "message"),
  #("sensors", "random_"),
  #("processors", "trigger"),
  #("processors", "toggle"),
  #("processors", "switch"),
  #("processors", "if_"),
  #("processors", "python"),
  ("processors", "advanced_python"),
  ("processors", "pull_buffer"),
  ("processors", "transistor"),
  ("processors", "push_buffer"),
  #("assessors", "not_"),
  #("assessors", "any_"),
  #("assessors", "all_"),
  #("assessors", "compare"),
  #("assessors", "between"),
  #("assessors", "variable"),
  #("assessors", "get_property"),
  #("assessors", "view"),
  ("assessors", "game_object"),
  #("assessors", "python"),
  #("rerouters", "hop_in"),
  #("rerouters", "hop_out"),
  #("rerouters", "splitter"),
  #("triggers", "start"),
  #("triggers", "always"),
  #("triggers", "if_"),
  #("triggers", "change"),
  #("triggers", "delay"),
  ("triggers", "stop"),
  ("triggers", "state_activate"),
  ("triggers", "state_deactivate"),
  #("actuators", "object"),
  #("actuators", "motion"),
  ("actuators", "view"),
  #("actuators", "launch"),
  #("actuators", "kill"),
  #("actuators", "pause"),
  #("actuators", "resume"),
  #("actuators", "stop"),
  #("actuators", "set_property"),
  #("actuators", "message"),
  #("actuators", "action"),
  #("actuators", "parent"),  
  ("actuators", "statemachine"),
  ("actuators", "state"),
)
def get_level(path):
  if path is None: return 0
  p = path[0]
  if p == "sparta": 
    if path[1:3] in advanced_sparta: return 2
    else: return 1
  if p in ("segments", "spyderbees"): return 0  #visibility depends on workergui/spydergui
  if p in ("hivemaps", "workers"): return 1
  if p in ("dragonfly","spydermaps"): return 3
  
  if p == "bees": 
    if len(path) == 1: return 0
    pp = path[1]
    if pp in ("parameter", "io"): return 3
    if pp in ("attribute", "pyattribute", "wasp", "part"): return 6
  
  return 6

def minlevel(context, level):
  try:
    currlevel = int(context.screen.hive_level)
  except:
    return False  
  return currlevel >= level
  
def active(context, path):
  return minlevel(context, get_level(path))
  
def active_workergui(context):
  return minlevel(context, 4)

def active_spydergui(context):
  return minlevel(context, 5)
  