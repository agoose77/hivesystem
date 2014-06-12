import os, sys

sys.path.insert(0, os.path.split(__file__)[0])

import spyder

os.mkdir("bee/hivemap/spycache")
spyder.loader.tempdir = "#PATH/spycache"
spyder.loader.recompile = None
spyder.load("basic")
import bee.hivemap

spyder.loader.export_wisdom("bee.hivemap")

import sys

sys.exit()
