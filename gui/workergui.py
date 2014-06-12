#!/usr/bin/env python

from __future__ import print_function, absolute_import

import os, sys, traceback, time

#readme = "hivegui-README.txt" 
#currdir = os.path.split(__file__)[0]
#if len(currdir): readme = currdir + os.sep + readme
#readmetxt = open(readme).read()

try:
  from hiveguilib import runworker
except ImportError:
  traceback.print_exc()
  if sys.platform == "win32":
    time.sleep(30)   
#runworker.run(readmetxt)
runworker.run()
