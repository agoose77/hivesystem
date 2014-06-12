
def generator_pythoncode(name, id, objs, forms, wrappings, defaultvalue):
  ret = []
  form = forms[0]
  if hasattr(form, "name"): name = form.name

  """
  ret.append('<item row="!!NEW-MEMBERPOS!!" column="0">')
  ret.append(' <widget class="QLabel" name="_head-%s">' % id)
  ret.append('  <property name="text">')
  ret.append('   <string>%s</string>' % name) 
  ret.append('  </property>')
  ret.append(' </widget>')
  ret.append('</item>')
  """
  ret.append('<item row="!!NEW-MEMBERPOS!!" column="0" colspan="2">')
  ret.append('<layout class="QVBoxLayout" name="_layout-%s">' % id)  
  ret.append('<item>')
  ret.append(' <widget class="QLabel" name="_head-%s">' % id)
  ret.append('  <property name="text">')
  ret.append('   <string>%s</string>' % name) 
  ret.append('  </property>')
  ret.append(' </widget>')
  ret.append('</item>')
  ret.append('<item>')
  ret.append(' <widget class="QTextEdit" name="_widget-%s">' % id)
  ret.append('  <property name="geometry">')
  ret.append('   <rect>') 
  ret.append('    <x>0</x>') 
  ret.append('    <y>0</y>') 
  ret.append('    <height>600</height>') 
  ret.append('    <width>600</width>') 
  ret.append('   </rect>') 
  ret.append('  </property>')
  ret.append('  <property name="minimumSize">')
  ret.append('   <size>') 
  ret.append('    <height>600</height>')   
  ret.append('    <width>600</width>') 
  ret.append('   </size>') 
  ret.append('  </property>')
  ret.append(' </widget>')
  ret.append('</item>')
  ret.append('</layout>')
  ret.append('</item>')

  return ret, [], [], []

from spyder.qtform.xml import set_element_generator
set_element_generator("pythoncode", generator_pythoncode)

try:
  import pygments
  from pygments.lexers import PythonLexer
  from pygments.formatters import HtmlFormatter
except ImportError:
  print("Warning: cannot locate pygments library. Python syntax highlighting disabled")
  pygments = None

callbacks = set()

running = False
def highlight(widget, *args):
  global running
  if pygments is None: return 
  if running == True: return
  cursor = widget.textCursor()
  pos = cursor.position()
  code = str(widget.toPlainText()).rstrip().rstrip("#") + "#"
  pos = min(pos, len(code))
  html = pygments.highlight(code, PythonLexer(), HtmlFormatter())  
  running = True
  widget.setHtml(html)
  cursor.setPosition(pos)
  widget.setTextCursor(cursor)  
  running = False

def set_css(widget):
  if pygments is None: return 
  css = HtmlFormatter().get_style_defs('.highlight')
  doc = widget.document()
  doc.setDefaultStyleSheet(css)
  
