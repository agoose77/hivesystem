from __future__ import absolute_import

from ..std.generator import generator
import random as random_module

def rand_gen(): 
  while 1:
    yield random_module.random()

random = generator("float", rand_gen)
