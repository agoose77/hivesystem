
def generator_objectlabel(name, id, objs, forms, wrappings, defaultvalue):
  ret = []
  form = forms[0]
  if hasattr(form, "name"): name = form.name

  typ = "object"
  tt = form._typetree
  if hasattr(tt, "fulltypename"): typ = str(tt.fulltypename)
  ret.append('<item row="!!NEW-MEMBERPOS!!" column="0">')
  ret.append(' <widget class="QLabel" name="_head-%s">' % id)
  ret.append('  <property name="text">')
  ret.append('   <string>%s</string>' % name) 
  ret.append('  </property>')
  ret.append(' </widget>')
  ret.append('</item>')
  ret.append('<item row="!!MEMBERPOS!!" column="1">')
  ret.append(' <widget class="QLabel" name="_typ-%s">' % id)
  ret.append('  <property name="text">')
  ret.append('   <string>&lt; type = %s &gt;</string>' % typ) 
  ret.append('  </property>')
  ret.append(' </widget>')
  ret.append('</item>')

  return ret, [], [], []

from spyder.qtform.xml import set_element_generator
set_element_generator("object", generator_objectlabel)
