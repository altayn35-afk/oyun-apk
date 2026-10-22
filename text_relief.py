"""Embossed live text: a light bevel, dark depth and original readable face."""
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.uix.button import Button


def enlarge(value):
    return sp(float(value[:-2])) * 1.10 if isinstance(value, str) and value.endswith('sp') else float(value) * 1.10


def relief(widget):
    if getattr(widget, '_relief', None):
        return widget
    widget._relief = TextRelief(widget)
    return widget


class TextRelief:
    def __init__(self, widget):
        self.widget = widget
        self.mask = None
        self.target_size = widget.font_size
        self.fitting = False
        self.update = Clock.create_trigger(self.refresh, 0)
        with widget.canvas.after:
            Color(.07, .10, .16, .72)
            self.shadow = Rectangle(size=(0, 0))
            Color(1, .98, .85, .85)
            self.bevel = Rectangle(size=(0, 0))
            Color(1, 1, 1, 1)
            self.face = Rectangle(size=(0, 0))
        widget.bind(texture=self.update, size=self.update, text=self.update,
                    text_size=self.update, font_name=self.update, bold=self.update,
                    font_size=self.font_changed, pos=self.position)
        self.update()

    def font_changed(self, widget, value):
        if not self.fitting:
            self.target_size = value
        self.update()

    def fit(self):
        w = self.widget
        if w.width <= dp(10) or w.height <= dp(10) or not w.text:
            return
        width = max(dp(1), (w.text_size[0] or w.width) - dp(4))
        height = max(dp(1), min(w.height, w.text_size[1] or w.height) - dp(4))
        size = self.target_size
        minimum = min(size, max(sp(11), size * .65))
        while True:
            probe = CoreLabel(text=w.text, font_name=w.font_name, font_size=size,
                              bold=w.bold, italic=w.italic,
                              text_size=(None if isinstance(w, Button) else width, None),
                              line_height=w.line_height)
            probe.refresh()
            if (probe.texture.height <= height and
                    (not isinstance(w, Button) or probe.texture.width <= width)) or size <= minimum:
                break
            size = max(minimum, size - sp(.5))
        if abs(w.font_size-size) > .01:
            self.fitting = True
            w.font_size = size
            self.fitting = False

    def refresh(self, *_):
        w = self.widget
        if w.texture is None or not w.text:
            for rect in (self.shadow, self.bevel, self.face):
                rect.size = (0, 0)
            return
        self.fit()
        self.mask = CoreLabel(text=w.text, font_name=w.font_name, font_size=w.font_size,
                              bold=w.bold, italic=w.italic, text_size=w.text_size,
                              halign=w.halign, valign=w.valign, padding=w.padding,
                              line_height=w.line_height, color=(1, 1, 1, 1))
        self.mask.refresh()
        self.shadow.texture = self.bevel.texture = self.mask.texture
        self.shadow.size = self.bevel.size = self.mask.texture.size
        self.face.texture = w.texture
        self.face.size = w.texture.size
        self.position()

    def position(self, *_):
        w = self.widget
        for rect, dx, dy in ((self.shadow, dp(.9), -dp(1.3)),
                             (self.bevel, -dp(.6), dp(.8)), (self.face, 0, 0)):
            rect.pos = (int(w.center_x - rect.size[0]/2) + dx,
                        int(w.center_y - rect.size[1]/2) + dy)
