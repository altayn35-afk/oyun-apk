"""Responsive real widgets; artwork never contains UI labels or statistics."""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
from menu_motion import MenuIcon
from text_relief import relief, enlarge
from pathlib import Path
from kivy.graphics import Color, RoundedRectangle

A = Path(__file__).parent / "assets"
TITLES = {
    "balon": "Balon Patlatma",
    "ari": "Bal Peşinde Neşeli Arı",
    "sekil": "Şekil ve Renk Avcısı",
    "bulmaca": "Süper Bulmaca",
}



def label(text, **kw):
    kw.setdefault("font_size", "17sp")
    kw["font_size"] = enlarge(kw["font_size"])

    # Renkli, kalın ve okunabilir oyun yazıları
    title = str(text).lower()

    if "minik kaşifler" in title:
        color = (1.0, 0.68, 0.08, 1)
    elif "merhaba" in title:
        color = (0.12, 0.48, 0.95, 1)
    elif "canların bitti" in title or "oyun bitti" in title:
        color = (0.95, 0.23, 0.30, 1)
    elif "başarı" in title or "seviye" in title:
        color = (0.56, 0.24, 0.90, 1)
    else:
        color = (0.16, 0.34, 0.75, 1)

    w = Label(
        text=text,
        color=color,
        bold=True,
        outline_width=1,
        outline_color=(1, 1, 1, 0.95),
        **kw
    )

    w.bind(
        size=lambda w, v: setattr(
            w, "text_size", (v[0], None)
        )
    )
    w.halign = "center"
    w.valign = "middle"

    return w



def button(text, fn, skin="button", **kw):
    b = Button(
                text=text,
        bold=True,
        color=(1, 1, 1, 1),
        outline_width=1,
        outline_color=(0.16, 0.12, 0.42, 1),
        halign="center",
        valign="middle",
        font_size="18sp",
        background_normal=str(A / (skin + ".png")),
        background_down=str(A / (skin + ".png")),
        border=(0, 0, 0, 0),
        **kw,
    )
    b.bind(on_release=lambda *_: fn())
    b.bind(size=lambda w, v: setattr(w, "text_size", (v[0] - dp(12), v[1])))
        return b


def backdrop(file):
    f = FloatLayout()
    f.add_widget(Image(source=str(A / file), fit_mode="cover"))
    return f


def cream(w):
    with w.canvas.before:
        Color(1, 0.97, 0.86, 0.92)
        rect = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(22)])
    w.bind(
        pos=lambda w, v: setattr(rect, "pos", v),
        size=lambda w, v: setattr(rect, "size", v),
    )
    return w


def panel(root):
    b = BoxLayout(
        orientation="vertical",
        padding=dp(18),
        spacing=dp(10),
        size_hint=(0.94, 0.92),
        pos_hint={"center_x": 0.5, "center_y": 0.5},
    )
    cream(b)
    root.add_widget(b)
    return b


def dialog(title, lines, actions, stars=None):
    """Illustrated modal with large controls and stars earned in the actual session."""
    root = backdrop("forest.jpg")
    body = BoxLayout(
        orientation="vertical",
        padding=dp(14),
        spacing=dp(8),
        size_hint=(0.94, 0.94),
        pos_hint={"center_x": 0.5, "center_y": 0.5},
    )
    cream(body)
    root.add_widget(body)
    body.add_widget(label(title, font_size="22sp", size_hint_y=None, height=dp(58)))
    art = BoxLayout(spacing=dp(8))
    if stars is not None:
        for i in range(3):
            art.add_widget(
                Image(
                    source=str(A / "sekil_Yildiz_Sari.png"),
                    fit_mode="contain",
                    color=(1, 1, 1, 1) if i < stars else (0.45, 0.45, 0.5, 0.32),
                )
            )
    else:
        art.add_widget(
            Image(
                source=str(
                    A
                    / (
                        "kart_Panda.png"
                        if title == "Oyun Bitti"
                        else "ari_karakter.png"
                    )
                ),
                fit_mode="contain",
            )
        )
    body.add_widget(art)
    body.add_widget(label(lines, size_hint_y=1.1))
    p = ModalView(
        size_hint=(0.94, None),
        height=min(Window.height * 0.94, dp(550)),
        auto_dismiss=False,
        background_color=(0, 0, 0, 0),
    )
    p._action_used = False
    p.content = root
    p.add_widget(root)
    for i, (text, fn) in enumerate(actions):

        def activate(fn=fn):
            if p._action_used:
                return
            p._action_used = True
            p.dismiss(animation=False)
            App.get_running_app().modal = None
            fn()

        body.add_widget(
            button(
                text,
                activate,
                skin=("button", "button_blue", "button_purple")[min(i, 2)],
                size_hint_y=None,
                height=dp(52),
            )
        )
    p.open()
    return p


class Login(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        r = backdrop("welcome.jpg")
        self.add_widget(r)
        b = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(16),
            size_hint=(0.92, None),
            height=dp(262),
            pos_hint={"center_x": 0.5, "top": 0.96},
        )
        cream(b)
        b.add_widget(
            label(
                "Minik Kaşifler\nAtölyesi",
                font_size="25sp",
                size_hint_y=None,
                height=dp(68),
            )
        )
        b.add_widget(label("Adını yazalım", size_hint_y=None, height=dp(30)))
        self.isim_kutusu = TextInput(
            multiline=False,
            font_size="24sp",
            hint_text="Adın",
            halign="center",
            size_hint_y=None,
            height=dp(48),
        )
        self.isim_kutusu.bind(on_text_validate=lambda *_: self.start())
        b.add_widget(self.isim_kutusu)
        b.add_widget(button("Başla", self.start, size_hint_y=None, height=dp(54)))
        r.add_widget(b)

    def on_pre_enter(self, *_):
        self.isim_kutusu.text = App.get_running_app().kayit.data["name"]

    def start(self):
        a = App.get_running_app()
        a.kayit.data["name"] = self.isim_kutusu.text.strip()[:20] or "Minik Kaşif"
        a.kayit.save()
        self.isim_kutusu.focus = False
        self.manager.current = "menu"


class Menu(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        r = backdrop("meadow.jpg")
        self.add_widget(r)
        b = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10),
                      size_hint=(0.96, 0.96),
                      pos_hint={"center_x": 0.5, "center_y": 0.5})
        r.add_widget(b)
        top = cream(BoxLayout(size_hint_y=None, height=dp(64), padding=dp(4)))
        self.greeting = label("", font_size="18sp")
        top.add_widget(self.greeting)
        top.add_widget(button("⚙", lambda: setattr(self.manager, "current", "settings"),
                              size_hint=(None, 1), width=dp(54)))
        b.add_widget(top)
        cards = GridLayout(cols=2, spacing=dp(10))
        icons = {"balon": "balon_kirmizi.png", "ari": "ari_karakter.png",
                 "sekil": "sekil_Yildiz_Mavi.png", "bulmaca": "kart_Aslan.png"}
        skins = {"balon": "tile", "ari": "tile_orange", "sekil": "tile_pink", "bulmaca": "tile_purple"}
        self.game_buttons = {}
        self.menu_icons = {}
        self._animation_event = None
        for g, title in TITLES.items():
            card = FloatLayout()
            control = button("", lambda g=g: App.get_running_app().start_game(g),
                             skin=skins[g], pos_hint={"x": 0, "y": 0})
            self.game_buttons[g] = control
            card.add_widget(control)
            self.menu_icons[g] = MenuIcon(g, icons[g], size_hint=(0.76, 0.59),
                                          pos_hint={"center_x": 0.5, "top": 0.93})
            card.add_widget(self.menu_icons[g])
            caption = label(title.replace("Peşinde ", "Peşinde\n").replace("Şekil ve Renk Avcısı", "Şekil ve\nRenk Avcısı"), font_size="15sp", size_hint=(0.88, 0.31),
                            pos_hint={"center_x": 0.5, "y": 0.08})
            caption.color = (1, 1, 1, 1)
            card.add_widget(caption)
            cards.add_widget(card)
        b.add_widget(cards)
        self.summary = label("", font_size="14sp", size_hint_y=None, height=dp(64))
        cream(self.summary)
        b.add_widget(self.summary)
        b.add_widget(button("Başarılarım", lambda: setattr(self.manager, "current", "achievements"),
                            size_hint_y=None, height=dp(52)))

    def on_enter(self, *_):
        self.start_animation()

    def on_pre_leave(self, *_):
        self.stop_animation()

    def on_leave(self, *_):
        self.stop_animation()

    def start_animation(self):
        if self._animation_event is None:
            self._animation_event = Clock.schedule_interval(self.animate, 1 / 30)

    def stop_animation(self):
        if self._animation_event:
            self._animation_event.cancel()
            self._animation_event = None

    def animate(self, dt):
        if self.manager and self.manager.current == self.name:
            for icon in self.menu_icons.values():
                icon.advance(dt)

    def on_pre_enter(self, *_):
        data = App.get_running_app().kayit.data
        self.greeting.text = "Merhaba " + data["name"] + "!"
        games = data["games"].values()
        self.summary.text = (f"En iyi puanlar: {sum(g['best'] for g in games)}\n"
                             f"Tamamlanan: {sum(g['completed'] for g in games)}  •  "
                             f"Yıldız: {sum(g['stars'] for g in games)}")


class Achievements(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        r = backdrop("meadow.jpg")
        self.add_widget(r)
        b = panel(r)
        b.add_widget(label("Başarılarım", font_size="25sp", size_hint_y=None, height=dp(48)))
        scroll = ScrollView(do_scroll_x=False)
        rows = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        rows.bind(minimum_height=rows.setter("height"))
        scroll.add_widget(rows)
        b.add_widget(scroll)
        self.rows = {}
        icons = {
            "balon": "balon_kirmizi.png",
            "ari": "ari_karakter.png",
            "sekil": "sekil_Yildiz_Mavi.png",
            "bulmaca": "kart_Aslan.png",
        }
        for g in TITLES:
            row = BoxLayout(padding=dp(6), spacing=dp(8), size_hint_y=None, height=dp(108))
            cream(row)
            row.add_widget(
                Image(source=str(A / icons[g]), size_hint_x=0.22, fit_mode="contain")
            )
            self.rows[g] = label("", font_size="15sp")
            row.add_widget(self.rows[g])
            rows.add_widget(row)
        b.add_widget(
            button("Ana Menü", lambda: setattr(self.manager, "current", "menu"), size_hint_y=None, height=dp(56))
        )

    def on_pre_enter(self, *_):
        for g, w in self.rows.items():
            d = App.get_running_app().kayit.data["games"][g]
            w.text = f"{TITLES[g]}\nEn iyi: {d['best']} • Seviye: {d['level']}\nTamamlanan: {d['completed']}\nYıldız: {d['stars']}"


class Settings(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        r = backdrop("meadow.jpg")
        self.add_widget(r)
        b = panel(r)
        b.add_widget(label("Ayarlar", font_size="27sp", size_hint_y=0.65))
        b.add_widget(
            Image(
                source=str(A / "ari_karakter.png"), fit_mode="contain", size_hint_y=0.8
            )
        )
        self.options = {}
        for k in ("sound", "music"):
            self.options[k] = button("", lambda k=k: self.toggle(k))
            b.add_widget(self.options[k])
        b.add_widget(
            button("Adımı değiştir", lambda: setattr(self.manager, "current", "giris"))
        )
        b.add_widget(
            button("Ana Menü", lambda: setattr(self.manager, "current", "menu"))
        )

    def on_pre_enter(self, *_):
        d = App.get_running_app().kayit.data
        for k, w in self.options.items():
            w.background_normal = str(
                A / ("button.png" if d[k] else "button_purple.png")
            )
            w.background_down = w.background_normal
            w.text = ("Ses efektleri" if k == "sound" else "Müzik") + (
                ": Açık" if d[k] else ": Kapalı"
            )

    def toggle(self, k):
        a = App.get_running_app()
        a.kayit.data[k] = not a.kayit.data[k]
        a.kayit.save()
        a.apply_audio()
        self.on_pre_enter()
