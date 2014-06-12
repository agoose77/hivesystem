import bpy
from .BlenderWidgets import BlenderWidget, define_widget_button


def same(id1, id2):
    if id1 is id2: return True
    if id1 is None or id2 is None: return False
    return id1.as_pointer() == id2.as_pointer()


class BlenderTextWidget(BlenderWidget):
    def __init__(self, parent, name, advanced=False):
        self.name = name
        self.value = None
        self.widget_id = define_widget_button(self.press)
        self._listeners = []
        self.advanced = advanced
        BlenderWidget.__init__(self, parent)

    def listen(self, callback):
        self._listeners.append(callback)

    def unlisten(self, callback):
        self._listeners.remove(callback)

    def block(self):
        self._blockedcount += 1

    def unblock(self):
        self._blockedcount -= 1
        if self._blockedcount < 0: self._blockedcount = 0

    def press(self):
        manager.set_text(self.value, self.set)

    def set(self, value):
        self.value = value
        for callback in self._listeners: callback(self.value)

    def get(self):
        return self.value

    def get2(self):
        if self.value is None: return ""
        return str(self.value)

    def draw2(self, context, layout):
        if self.name is not None:
            layout = layout.row()
            layout.label("TEXT_WIDGET" + str(self.name))
        layout.operator(self.widget_id, "Edit in Text Editor")

    def show(self):
        self.press()


class BlenderTextManager:
    def __init__(self, textblock):
        self.textblock = textblock
        self.space = None
        self.clear()

    def check_area(self):
        if self.area is None: return False
        areas = bpy.context.screen.areas
        for area in areas:
            if same(area, self.area):
                if area.type == "TEXT_EDITOR":
                    return True
                else:
                    return False
        return False

    def find_area(self):
        # if a previously-claimed area is still there, use it
        if self.check_area(): return

        #find a new area
        self.clear()
        areas = bpy.context.screen.areas
        ar_text = []
        ar_other = []
        for area in areas:
            if area.type == "NODE_EDITOR": continue
            ar = ar_text if area.type == "TEXT_EDITOR" else ar_other
            size = area.height * area.width
            ar.append((area, size))
        #first try to find a Text Editor area, then a non-Text Editor
        area = None
        for ar in ar_text, ar_other:
            if not len(ar): continue
            #select the largest area
            ar.sort(key=lambda a: -a[1])
            area = ar[0][0]
            break
        if area is None: return  #no areas...

        self.area = area
        self.area.type = "TEXT_EDITOR"
        self.space = self.area.spaces[0]

    def set_text(self, value, setter):
        self.find_area()
        self.setter = None
        block = bpy.data.texts.get(self.textblock)
        if block is None: block = bpy.data.texts.new(self.textblock)
        block.from_string(str(value))
        self.space.text = block
        self.lastvalue = value
        self.setter = setter

    def clear(self):
        if self.space is not None:
            self.space.text.from_string("")
        self.area = None
        self.space = None
        self.lastvalue = None
        self.setter = None

    def select(self, ids):
        # Whenever the selection changes, clear
        self.clear()

    def check_update(self):
        if self.area is None: return
        if self.space is None: return
        if self.setter is None: return
        if self.space.text.name != self.textblock:
            self.clear()
            return
        t = self.space.text.as_string()
        if self.lastvalue != t:
            self.lastvalue = t
            self.setter(t)


manager = BlenderTextManager("HiveGUI Text Property")