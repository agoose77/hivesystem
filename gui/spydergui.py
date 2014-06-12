#!/usr/bin/env python

from __future__ import print_function, absolute_import

import os, sys, traceback, time

try:
  from hiveguilib import runspyder
except ImportError:
  traceback.print_exc()
  if sys.platform == "win32":
    time.sleep(30)   
runspyder.run()
