"""Menu-only sprite animation; no game rules or touch targets live here."""
import math
from pathlib import Path
from kivy.uix.widget import Widget
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle

ASSETS = Path(__file__).parent / 'assets'


class MenuIcon(Widget):
    def __init__(self, game, source, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.elapsed = 0.0
        prefix = {'ari': 'menu_ari', 'bulmaca': 'menu_aslan'}.get(game)
        files = [f'{prefix}_{i}.png' for i in range(4)] if prefix else [source]
        self.frames = [CoreImage(str(ASSETS / f)).texture for f in files]
        self.frame_index = 0
        with self.canvas:
            Color(1, 1, 1, 1)
            self.art = Rectangle(texture=self.frames[0])
        self.bind(pos=self.redraw, size=self.redraw)
        self.redraw()

    def advance(self, dt):
        self.elapsed += max(0, dt)
        self.redraw()

    def redraw(self, *_):
        t = self.elapsed
        fps = 12 if self.game == 'ari' else 7
        self.frame_index = int(t * fps) % len(self.frames)
        tex = self.frames[self.frame_index]
        scale = .90
        dx = dy = 0
        if self.game == 'balon':
            dy = math.sin(t * 2.4) * self.height * .055
        elif self.game == 'sekil':
            scale = .84 + .07 * math.sin(t * 2.5)
            dx = math.sin(t * 2.5) * self.width * .025
        elif self.game == 'bulmaca':
            dx = math.sin(t * 1.6) * self.width * .045
            dy = abs(math.sin(t * 7)) * self.height * .012
        ratio = min(self.width * scale / tex.width, self.height * scale / tex.height)
        w, h = tex.width * ratio, tex.height * ratio
        self.art.texture = tex
        self.art.size = (w, h)
        self.art.pos = (self.center_x - w / 2 + dx, self.center_y - h / 2 + dy)
