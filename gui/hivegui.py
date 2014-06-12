#!/usr/bin/env python

from __future__ import print_function, absolute_import

import os, sys, traceback, time

readmetxt = None
if "--debug" not in sys.argv:
  readme = "hivegui-README.txt" 
  currdir = os.path.split(__file__)[0]
  if len(currdir): readme = currdir + os.sep + readme
  readmetxt = open(readme).read()
else:
  sys.argv = [a for a in sys.argv if a != "--debug"]
  
try:
  from hiveguilib import run
except ImportError:
  traceback.print_exc()
  if sys.platform == "win32":
    time.sleep(30)   
run.run(readmetxt)
#run.run()
