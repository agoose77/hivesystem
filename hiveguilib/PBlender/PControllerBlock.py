import logging

class PControllerBlock(object):
  def __init__(self, parent):
    pass

  def set_blocktype(self, blocktype):
    logging.debug("PControllerBlock.set_blocktype, what to do?")

  def set_blockvalues(self, blockvalues):
    logging.debug("PControllerBlock.set_blockvalues, what to do?")

  def set_blockstrings(self, blockstrings):
    logging.debug("PControllerBlock.set_blockstrings, what to do?")

  def show(self):
    logging.debug("PControllerBlock.show, what to do?")

  def hide(self):
    logging.debug("PControllerBlock.hide, what to do?")
  
  def draw(self, context, layout):
    pass #TODO