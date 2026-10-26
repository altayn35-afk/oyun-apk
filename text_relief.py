
"""Clean, readable outlined lettering for Kivy Labels and Buttons."""

from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle
from kivy.metrics import sp


def enlarge(value):
    if isinstance(value, str) and value.endswith("sp"):
        return sp(float(value[:-2])) * 1.10
    return float(value) * 1.10


def relief(widget):
    if getattr(widget, "_relief", None):
        return widget
    widget._relief = TextRelief(widget)
    return widget


class TextRelief:
    def __init__(self, widget):
        self.widget = widget
        self.update = Clock.create_trigger(self.refresh, 0)

        with widget.canvas.after:
            Color(0.10, 0.13, 0.32, 0.75)
            self.shadow = Rectangle(size=(0, 0))
            Color(1, 1, 1, 1)
            self.face = Rectangle(size=(0, 0))

        widget.bind(
            texture=self.update,
            size=self.update,
            pos=self.position,
            text=self.update,
            text_size=self.update,
            font_name=self.update,
            font_size=self.update,
            bold=self.update,
            color=self.update,
        )
        self.update()

    def refresh(self, *_):
        w = self.widget

        if not w.text or w.texture is None:
            self.shadow.size = (0, 0)
            self.face.size = (0, 0)
            return

        mask = CoreLabel(
            text=w.text,
            font_name=w.font_name,
            font_size=w.font_size,
            bold=w.bold,
            italic=w.italic,
            text_size=w.text_size,
            halign=w.halign,
            valign=w.valign,
            padding=w.padding,
            line_height=w.line_height,
            color=(1, 1, 1, 1),
        )
        mask.refresh()

        self.shadow.texture = mask.texture
        self.shadow.size = mask.texture.size
        self.face.texture = w.texture
        self.face.size = w.texture.size
        self.position()

    def position(self, *_):
        w = self.widget
        self.shadow.pos = (
            w.center_x - self.shadow.width / 2 + 1,
            w.center_y - self.shadow.height / 2 - 1,
        )
        self.face.pos = (
            w.center_x - self.face.width / 2,
            w.center_y - self.face.height / 2,
        )
