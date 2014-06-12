from __future__ import print_function, absolute_import


class Hook(object):
    def __init__(self,
                 shape,
                 style,
                 color=(255, 255, 255),
                 tooltip=None,
                 hover_text=None,
                 order_dependent=False,
                 visible=True
    ):
        assert shape in ("circle", "square")
        self.shape = shape
        assert style in ("solid", "dashed", "dot")
        self.style = style
        self.color = color
        self.tooltip = tooltip
        assert visible in (True, False)
        self.hover_text = hover_text
        self.order_dependent = order_dependent
        self.visible = visible


class Attribute(object):
    def __init__(self,
                 name,
                 inhook,
                 outhook,
                 label=None,
                 value=None,
                 value_on_newline=False,
                 tooltip=None,
                 visible=True
    ):
        self.name = name
        assert inhook is None or isinstance(inhook, Hook)
        self.inhook = inhook
        assert outhook is None or isinstance(outhook, Hook)
        self.outhook = outhook
        self.label = label
        assert value is None or isinstance(value, str)
        self.value = value
        self.value_on_newline = value_on_newline
        self.tooltip = tooltip
        assert visible in (True, False)
        self.visible = visible
    
