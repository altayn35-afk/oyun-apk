# -*- coding: utf-8 -*-
"""
Minik Kaşifler Atölyesi — offline Android edition 1.3
"""

from startup_diagnostics import install as install_startup_diagnostics, mark
install_startup_diagnostics()
mark("import-kivy")

import math
import os
import random
import time

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from functools import lru_cache
from kivy.graphics import RoundedRectangle
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from text_relief import relief
from kivy.uix.stencilview import StencilView
from kivy.metrics import dp
from kivy.core.text import LabelBase
from storage import SaveStore
from kivy.graphics import Color, Ellipse, Rectangle, Triangle, Line
from kivy.clock import Clock
from kivy.animation import Animation
from rewarded_ads import RewardedAds
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
mark("imports-complete")

ASSETS_KLASORU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

class YuklemeEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.arkaplan = Image(
            source=os.path.join(ASSETS_KLASORU, "acilis_ekrani_bos.png"),
            fit_mode="fill",
            size_hint=(1, 1),
        )

        self.add_widget(self.arkaplan)
        self.yukleme_doluluk = 0
        self.yukleme_cubugu = Widget(
            size_hint=(None, None)
        )
        self.add_widget(self.yukleme_cubugu)
        with self.yukleme_cubugu.canvas:
            Color(1, 0.85, 0.05, 1)
            self.sari_dolum = RoundedRectangle(
                pos=(0, 0),
                size=(0, dp(20)),
                radius=[dp(10)]
            )
            
# ==========================================
# SES YONETIMI
# ==========================================
SES_ACIK = True
_SES_CACHE = {}


def _ses_dosyasi(ad):
    yol = os.path.join(ASSETS_KLASORU, ad)
    return yol if os.path.exists(yol) else None


def ses_efekti_cal(ses_tipi):
    if not SES_ACIK:
        return
    try:
        if ses_tipi in _SES_CACHE:
            s = _SES_CACHE[ses_tipi]
            s.stop()
            s.play()
            return
        dosya = _ses_dosyasi(f"{ses_tipi}.wav")
        if dosya:
            s = SoundLoader.load(dosya)
            if s:
                _SES_CACHE[ses_tipi] = s
                s.play()
    except Exception as e:
        print(f"Ses hatasi: {e}")


_MUZIK = None


def muzik_baslat():
    global _MUZIK
    if not App.get_running_app().kayit.data["music"]:
        return
    if _MUZIK:
        _MUZIK.play()
        return
    dosya = _ses_dosyasi("fon_muzigi.wav")
    if not dosya:
        kok = os.path.dirname(os.path.abspath(__file__))
        for f in os.listdir(kok):
            if f.lower().endswith(".mp3"):
                dosya = os.path.join(kok, f)
                break
    if dosya:
        try:
            _MUZIK = SoundLoader.load(dosya)
            if _MUZIK:
                _MUZIK.loop = True
                _MUZIK.volume = 0.5
                _MUZIK.play()
        except Exception as e:
            print(f"Muzik hatasi: {e}")


def muzik_ses_seviyesi_ayarla(seviye):
    if _MUZIK:
        try:
            _MUZIK.volume = seviye
        except Exception:
            pass


def metni_turkce_seslendir(metin, bitince_bunu_yap=None):
    # Offline sürüm: ağdan ses indirilmez.
    if bitince_bunu_yap:
        bitince_bunu_yap()


@lru_cache(maxsize=96)
def oyun_dokusu(dosya):
    """Reuse GPU textures instead of decoding image files on every animation frame."""
    yol = os.path.join(ASSETS_KLASORU, dosya)
    return CoreImage(yol).texture if os.path.isfile(yol) else None


# ==========================================
# ORTAK RENKLER / YARDIMCILAR
# ==========================================
BALON_RENKLERI = [
    (1, 0.30, 0.30, 1),
    (0.30, 0.58, 1, 1),
    (0.30, 1, 0.53, 1),
    (1, 0.84, 0.20, 1),
    (0.70, 0.40, 1, 1),
    (1, 0.60, 0.20, 1),
]

RENK_SOZLUGU = {
    "Kirmizi": (1, 0.2, 0.2, 1),
    "Yesil": (0.18, 0.80, 0.44, 1),
    "Mavi": (0.20, 0.60, 0.86, 1),
    "Turuncu": (0.90, 0.49, 0.13, 1),
    "Mor": (0.61, 0.35, 0.71, 1),
    "Sari": (0.95, 0.77, 0.06, 1),
}
SEKIL_TIPLERI = ["Yuvarlak", "Kare", "Ucgen", "Yildiz"]


def format_sure(saniye):
    saniye = max(0, int(saniye))
    return f"{saniye // 60}:{saniye % 60:02d}"


class KalpGostergesi(Widget):
    def __init__(self, canlar=0, maxcan=3, **kwargs):
        super().__init__(**kwargs)
        self.canlar = canlar
        self.maxcan = maxcan
        self.bind(size=self._ciz, pos=self._ciz)

    def guncelle(self, canlar, maxcan):
        self.canlar = canlar
        self.maxcan = maxcan
        self._ciz()

    @staticmethod
    def _tek_kalp(cx, cy, b, dolu):
        r = b * 0.27
        if dolu:
            Color(0.90, 0.18, 0.22, 1)
        else:
            Color(0.72, 0.72, 0.76, 1)
        Ellipse(pos=(cx - r * 1.9, cy - r * 0.25), size=(r * 2, r * 2))
        Ellipse(pos=(cx - r * 0.1, cy - r * 0.25), size=(r * 2, r * 2))
        Triangle(
            points=[
                cx - r * 1.85,
                cy + r * 0.35,
                cx + r * 1.85,
                cy + r * 0.35,
                cx,
                cy - b * 0.42,
            ]
        )

    def _ciz(self, *a):
        self.canvas.clear()
        w, h = self.size
        if w <= 1 or h <= 1 or self.maxcan <= 0:
            return
        with self.canvas:
            boyut = min(h * 0.9, w / self.maxcan * 0.9)
            bosluk = max(2, (w - boyut * self.maxcan) / (self.maxcan + 1))
            for i in range(self.maxcan):
                cx = self.x + bosluk * (i + 1) + boyut * i + boyut / 2
                cy = self.y + h / 2
                self._tek_kalp(cx, cy, boyut, i < self.canlar)


class BalonOyunuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = OyunArkaplani("meadow.jpg")
        self.dis = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(5))

        # Kompakt/Kucultulmus Oyun Alani Container'i
        self.cerceve = FloatLayout(size_hint=(1, 0.70))
        self.oyun_alani = StencilView(
            size_hint=(0.98, 0.98), pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.oyun_alani.bind(on_touch_down=self.dokunuldu)
        self.oyun_alani.bind(size=lambda *_: None)
        self.cerceve.add_widget(self.oyun_alani)

        self.lbl_skor = Label(
            text="Puan: 0 | Seviye: 1",
            size_hint=(1, None),
            height=dp(60),
            color=(1, 1, 1, 1),
            bold=True,
            outline_width=1,
            outline_color=(0.12, 0.24, 0.14, 1),
        )

        self.dis.add_widget(self.lbl_skor)
        self.dis.add_widget(self.cerceve)
        self.kok.add_widget(self.dis)
        self.add_widget(self.kok)
        self.ust_panel = None
        self._olay = None
        self.balonlar = []

    def _panel_kur(self):
        if self.ust_panel is None:
            self.ust_panel = UstPanel(self.app, self.menuye_don)
            self.dis.add_widget(self.ust_panel, index=len(self.dis.children))

    def menuye_don(self):
        self.oyun_aktif = False
        if self._olay:
            self._olay.cancel()
        self.manager.current = "menu"

    def oyunu_baslat(self):
        self.app = App.get_running_app()
        self._panel_kur()
        self.puan = 0
        self.seviye = 1
        self.balon_sayaci = 0
        self.seviye_balonlari = 0
        self.oyun_aktif = True
        # A newly selected Screen can still have a zero-height play area before layout.
        # Save the same nonzero viewport used to create positions AND velocities.
        w = self.oyun_alani.width if self.oyun_alani.width > 1 else dp(350)
        h = self.oyun_alani.height if self.oyun_alani.height > 1 else dp(450)
        self.balonlar = [
            {"x": w*x, "y": h*y, "hiz": h*.158, "aci": i,
             "sprite": color, "tuzak": False}
            for i, (x, y, color) in enumerate(((.24,.15,"mavi"),(.74,.43,"sari"),(.30,.71,"kirmizi")))
        ]
        self._last_size = (w, h)
        muzik_ses_seviyesi_ayarla(0.2)
        if self._olay:
            self._olay.cancel()
        self._olay = Clock.schedule_interval(self.adim, 1 / 30)

    def adim(self, dt):
        if not self.oyun_aktif or self.manager.current != self.name:
            return
        w, h = self.oyun_alani.size
        if w <= 1 or h <= 1:
            return

        oldw, oldh = self._last_size
        if oldw > 0 and oldh > 0 and (oldw, oldh) != (w, h):
            for balloon in self.balonlar:
                balloon["x"] *= w / oldw
                balloon["y"] *= h / oldh
                balloon["hiz"] *= h / oldh
        self._last_size = (w, h)
        # Spacing is relative to the viewport, including high density Android displays.
        if random.random() < min(1, dt * (0.65 + self.seviye * 0.07)) and not any(
            b["y"] < w * 0.43 for b in self.balonlar
        ):
            self.balon_sayaci += 1
            tuzak = self.balon_sayaci % 7 == 0  # Her 7-8 balon bir tuzak balon!
            self.balonlar.append(
                {
                    "x": random.uniform(w * 0.14, w * 0.86),
                    "y": -w * 0.20,
                    "hiz": h * min(0.42, 0.14 + self.seviye * 0.018),
                    "renk": (
                        (0.1, 0.1, 0.1, 1) if tuzak else random.choice(BALON_RENKLERI)
                    ),
                    "sprite": (
                        "tuzak"
                        if tuzak
                        else random.choice(
                            ["kirmizi", "mavi", "yesil", "sari", "mor", "turuncu"]
                        )
                    ),
                    "tuzak": tuzak,
                    "aci": random.uniform(0, 10),
                }
            )

        # Seviyeye gecildiginde ekrandaki balonlar da hizlansin.
        yeni_balonlar = []
        for b in self.balonlar:
            if b["hiz"] <= 0:
                b["hiz"] = h * min(0.42, 0.14 + self.seviye * 0.018)
            b["y"] += b["hiz"] * dt * (1 + (self.seviye - 1) * 0.14)
            b["aci"] += dt * 1.5
            b["x"] = max(
                w * 0.14, min(w * 0.86, b["x"] + math.sin(b["aci"]) * dt * w * 0.045)
            )
            if b["y"] < h + w * 0.2:
                yeni_balonlar.append(b)
            elif not b["tuzak"]:
                self._can_azalt()
                if not self.oyun_aktif:
                    break
        self.balonlar = yeni_balonlar

        # Cizim
        self.oyun_alani.canvas.clear()
        with self.oyun_alani.canvas:
            for b in self.balonlar:
                r = self.oyun_alani.width * 0.13
                Color(1, 1, 1, 1)
                texture = oyun_dokusu("balon_" + b["sprite"] + ".png")
                Rectangle(
                    texture=texture,
                    pos=(
                        self.oyun_alani.x + b["x"] - r,
                        self.oyun_alani.y + b["y"] - r * 1.45,
                    ),
                    size=(r * 2, r * 2.95),
                )

    def dokunuldu(self, inst, touch):
        if not getattr(self, "oyun_aktif", False) or not self.oyun_alani.collide_point(
            *touch.pos
        ):
            return
        local_x = touch.x - self.oyun_alani.x
        local_y = touch.y - self.oyun_alani.y

        for b in self.balonlar[:]:
            if (
                abs(local_x - b["x"]) < (self.oyun_alani.width * 0.13)
                and abs(local_y - b["y"]) < (self.oyun_alani.width * 0.13) * 1.35
            ):
                if b["tuzak"]:
                    # Tuzak balona tiklandi! Can kaybet
                    ses_efekti_cal("uzuntu")
                    self.balonlar.remove(b)
                    self._can_azalt()
                else:
                    ses_efekti_cal("alkis")
                    self.puan += 10
                    self.seviye_balonlari += 1
                    self.balonlar.remove(b)
                    self.app.record(self)
                    self.app.effect(
                        self.oyun_alani.x + b["x"], self.oyun_alani.y + b["y"], "+10"
                    )
                    if self.seviye_balonlari >= 5 * self.seviye:
                        self.app.complete(self, self._sonraki_balon_seviyesi)
                    self.lbl_skor.text = (
                        f"Puan: {self.puan} | Seviye: {self.seviye} | "
                        f"Balon: {self.seviye_balonlari}/{5 * self.seviye}"
                    )
                break

    def _sonraki_balon_seviyesi(self):
        self.seviye_balonlari = 0
        self.balonlar = []
        self.oyun_aktif = True

    def _can_azalt(self):
        self.app.canlar = max(0, self.app.canlar - 1)
        ses_efekti_cal("uzuntu")
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            if self._olay:
                self._olay.cancel()
            can_bitti_popup_goster(self.app, "balon", self.menuye_don)


# ==========================================
# OYUN 2: NESELI ARI (Ağaç Sorunu Çözüldü & Kovan Eklendi)
# ==========================================
class EnergyMeter(Widget):
    value = NumericProperty(4)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(value=self.draw, size=self.draw, pos=self.draw)

    def draw(self, *_):
        self.canvas.clear()
        gap = dp(4)
        width = max(0, (self.width - 3*gap)/4)
        with self.canvas:
            for i in range(4):
                Color(*((1, .66, .04, 1) if i < self.value else (.68, .67, .62, .7)))
                RoundedRectangle(pos=(self.x+i*(width+gap), self.y+dp(6)),
                                 size=(width, max(0,self.height-dp(12))), radius=[dp(5)])


class AriOyunuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = OyunArkaplani("forest.jpg")
        self.dis = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(5))
        self.oyun_alani = StencilView(size_hint=(1, 0.70))
        self.oyun_alani.bind(
            on_touch_move=self.parmak_hareket, on_touch_down=self.parmak_hareket
        )

        self.lbl_skor = Label(
            text="Puan: 0 | Seviye: 1",
            size_hint=(1, None),
            height=dp(60),
            color=(1, 1, 1, 1),
            bold=True,
            outline_width=1,
            outline_color=(0.12, 0.24, 0.14, 1),
        )
        self.dis.add_widget(self.lbl_skor)
        energy_row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(8), padding=(dp(8), 0))
        cream(energy_row)
        self.lbl_energy = label("Enerji: 4/4", font_size="14sp", size_hint_x=.45)
        self.energy_meter = EnergyMeter()
        energy_row.add_widget(self.lbl_energy)
        energy_row.add_widget(self.energy_meter)
        self.dis.add_widget(energy_row)
        self.dis.add_widget(self.oyun_alani)
        self.kok.add_widget(self.dis)
        self.add_widget(self.kok)
        self.ust_panel = None
        self._olay = None

    def _panel_kur(self):
        if self.ust_panel is None:
            self.ust_panel = UstPanel(self.app, self.menuye_don)
            self.dis.add_widget(self.ust_panel, index=len(self.dis.children))

    def menuye_don(self):
        self.oyun_aktif = False
        if self._olay:
            self._olay.cancel()
        self.manager.current = "menu"

    def oyunu_baslat(self):
        self.app = App.get_running_app()
        self._panel_kur()
        self.puan = 0
        self.seviye = 1
        self.engeller = [[.75, .5, True]]
        self.oyun_aktif = True
        muzik_ses_seviyesi_ayarla(0.2)
        if self._olay:
            self._olay.cancel()
        self._olay = Clock.schedule_interval(self.adim, 1 / 30)

        self.ari_y = 0.5
        self.ari_hedef_y = 0.5
        self.spawn = 0
        self.collected = 0
        self.energy = 4
        self.elapsed = 0
        self.invulnerable = 0

    def parmak_hareket(self, inst, touch):
        if getattr(self, "oyun_aktif", False) and self.oyun_alani.collide_point(
            *touch.pos
        ):
            self.ari_hedef_y = max(
                0.12,
                min(
                    0.88, (touch.y - self.oyun_alani.y) / max(1, self.oyun_alani.height)
                ),
            )
            return True

    def adim(self, dt):
        if not self.oyun_aktif or self.manager.current != self.name:
            return
        self.elapsed += dt
        self.ari_y += (self.ari_hedef_y - self.ari_y) * (1 - math.exp(-12 * dt))
        self.spawn -= dt
        self.invulnerable = max(0, self.invulnerable - dt)
        if self.spawn <= 0:
            self.engeller.append(
                [1.10, random.uniform(0.14, 0.86), random.random() < 0.75]
            )
            self.spawn = max(0.9, 1.7 - self.seviye * 0.08)
        speed = min(0.40, 0.17 + self.seviye * 0.018)
        for obj in self.engeller[:]:
            obj[0] -= speed * dt
            if obj[0] < -0.1:
                self.engeller.remove(obj)
                if obj[2]:
                    self.energy -= 1
                    if self.energy == 0:
                        self.energy = 4
                        self.app.effect(self.oyun_alani.center_x, self.oyun_alani.center_y,
                                        "Enerjin bitti! -1 can")
                        self._can_azalt()
                        if not self.oyun_aktif:
                            return
                continue
            if abs(obj[0] - 0.20) < 0.105 and abs(obj[1] - self.ari_y) < 0.085:
                self.engeller.remove(obj)
                if obj[2]:
                    self.puan += 10
                    self.collected += 1
                    self.energy = 4
                    ses_efekti_cal("tin")
                    self.app.record(self)
                    self.app.effect(
                        self.oyun_alani.x + self.oyun_alani.width * 0.2,
                        self.oyun_alani.y + self.oyun_alani.height * self.ari_y,
                        "+10",
                    )
                elif self.invulnerable <= 0:
                    self.invulnerable = 1.2
                    self._can_azalt()
                    if not self.oyun_aktif:
                        return
        self._ciz(0, 0)
        if self.collected >= 5 + self.seviye:
            self.puan += 30
            self.app.complete(self, self.next_level)

    def _ciz(self, *_):
        self.energy_meter.value = self.energy
        self.lbl_energy.text = f"Enerji: {self.energy}/4"
        a = self.oyun_alani
        w, h = a.size
        a.canvas.clear()
        with a.canvas:
            Color(1, 1, 1, 1)
            for x, y, honey in self.engeller:
                side = w * 0.20
                sw, sh = (side, side) if honey else (side * .75, side * 1.125)
                Rectangle(
                    texture=oyun_dokusu("honey.png" if honey else "balon_tuzak.png"),
                    pos=(a.x + x * w - sw / 2, a.y + y * h - sh / 2),
                    size=(sw, sh),
                )
            side = w * 0.31
            Color(1, 1, 1, 0.45 if self.invulnerable > 0 and int(self.elapsed * 12) % 2 else 1)
            Rectangle(
                texture=oyun_dokusu("ari_karakter.png"),
                pos=(
                    a.x + w * 0.20 - side / 2,
                    a.y
                    + h * self.ari_y
                    - side / 2
                    + math.sin(self.elapsed * 15) * h * 0.007,
                ),
                size=(side, side),
            )
            Color(1, 1, 1, 1)
            Rectangle(
                texture=oyun_dokusu("kovan.png"),
                pos=(a.right - w * 0.19, a.y),
                size=(w * 0.18, w * 0.22),
            )
        self.lbl_skor.text = f"Puan: {self.puan} | Seviye: {self.seviye}\nBal: {self.collected}/{5+self.seviye} • Parmağınla yönlendir"

    def _can_azalt(self):
        self.app.canlar = max(0, self.app.canlar - 1)
        ses_efekti_cal("uzuntu")
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            if self._olay:
                self._olay.cancel()
            can_bitti_popup_goster(self.app, "ari", self.menuye_don)

    def next_level(self):
        self.collected = 0
        self.energy = 4
        self.engeller = []
        self.spawn = 0.8
        self.oyun_aktif = True


# ==========================================
# OYUN 3: SEKIL VE RENK AVCISI (Büyük İkonlar & Adet Gösterimi)
# ==========================================
class SekilOyunuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = OyunArkaplani("shapes.jpg")
        self.dis = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(5))

        self.lbl_soru = Label(
            text="",
            size_hint=(1, None),
            height=dp(64),
            bold=True,
            color=(1, 1, 1, 1),
            font_size="17sp",
            outline_width=2,
            outline_color=(0.12, 0.25, 0.19, 1),
        )
        self.lbl_durum = Label(
            text="",
            size_hint=(1, None),
            height=dp(44),
            color=(1, 1, 1, 1),
            bold=True,
            outline_width=1,
            outline_color=(0.1, 0.25, 0.15, 1),
        )

        self.cerceve = FloatLayout(size_hint=(1, 0.70))
        self.oyun_alani = StencilView(
            size_hint=(0.98, 0.96), pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.oyun_alani.bind(on_touch_down=self.dokunuldu)
        self.oyun_alani.bind(
            pos=lambda *_: (self._konumlandir_ve_ciz() if getattr(self, "nesneler", None) else None),
            size=lambda *_: (
                self._konumlandir_ve_ciz() if getattr(self, "nesneler", None) else None
            )
        )
        self.cerceve.add_widget(self.oyun_alani)

        task = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(8), padding=dp(4))
        self.target_art = Image(size_hint_x=None, width=dp(58), fit_mode="contain")
        task.add_widget(self.target_art)
        self.lbl_soru.size_hint_y = 1
        task.add_widget(self.lbl_soru)
        cream(task)
        self.dis.add_widget(task)
        self.dis.add_widget(self.lbl_durum)
        self.dis.add_widget(self.cerceve)
        self.kok.add_widget(self.dis)
        self.add_widget(self.kok)
        self.ust_panel = None
        self._zaman_olay = None
        self.nesneler = []

    def _panel_kur(self):
        if self.ust_panel is None:
            self.ust_panel = UstPanel(self.app, self.menuye_don)
            self.dis.add_widget(self.ust_panel, index=len(self.dis.children))

    def menuye_don(self):
        self.oyun_aktif = False
        if self._zaman_olay:
            self._zaman_olay.cancel()
        self.manager.current = "menu"

    def oyunu_baslat(self):
        self.app = App.get_running_app()
        self._panel_kur()
        self.seviye = 1
        self.puan = 0
        muzik_ses_seviyesi_ayarla(0.2)
        self._seviye_yukle()

    def _seviye_yukle(self):
        self.oyun_aktif = True
        self.kalan_sure = max(10, 25 - self.seviye)
        self.bulunan = 0

        self.hedef_renk_adi = random.choice(list(RENK_SOZLUGU.keys()))
        self.hedef_renk = RENK_SOZLUGU[self.hedef_renk_adi]
        self.hedef_sekil = random.choice(SEKIL_TIPLERI)
        self.hedef_sayi = random.randint(2, 4)

        self.nesneler = []
        for _ in range(self.hedef_sayi):
            self.nesneler.append(
                {
                    "renk": self.hedef_renk,
                    "sekil": self.hedef_sekil,
                    "hedef": True,
                    "bulundu": False,
                }
            )

        for _ in range(6):
            r_ad = random.choice(list(RENK_SOZLUGU.keys()))
            s_tip = random.choice(SEKIL_TIPLERI)
            if r_ad == self.hedef_renk_adi and s_tip == self.hedef_sekil:
                s_tip = "Kare" if self.hedef_sekil != "Kare" else "Yuvarlak"
            self.nesneler.append(
                {
                    "renk": RENK_SOZLUGU[r_ad],
                    "sekil": s_tip,
                    "hedef": False,
                    "bulundu": False,
                }
            )

        random.shuffle(self.nesneler)

        # Çocukların rahat anlaması için büyük yazı ve adet gösterimi
        self.target_art.source = os.path.join(ASSETS_KLASORU, f"sekil_{self.hedef_sekil}_{self.hedef_renk_adi}.png")
        self.lbl_soru.text = f"{TR[self.hedef_renk_adi]} {TR[self.hedef_sekil].lower()} bul!\n{self.hedef_sayi} tane"
        self.lbl_durum.text = (
            f"Seviye {self.seviye} | Puan {self.puan}"
        )

        Clock.schedule_once(lambda dt: self._konumlandir_ve_ciz(), 0)
        metni_turkce_seslendir(
            f"{self.hedef_sayi} tane {self.hedef_renk_adi} {self.hedef_sekil} bul"
        )
        if self._zaman_olay:
            self._zaman_olay.cancel()
        self._zaman_olay = Clock.schedule_interval(self._zaman_adimi, 1)

    def _konumlandir_ve_ciz(self):
        w = self.oyun_alani.width or 320
        h = self.oyun_alani.height or 350
        n_toplam = len(self.nesneler)
        cols = 3
        rows = math.ceil(n_toplam / cols)
        hucre_w, hucre_h = w / cols, h / rows

        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx >= len(self.nesneler):
                    break
                self.nesneler[idx]["x"] = c * hucre_w + hucre_w / 2
                self.nesneler[idx]["y"] = (rows - 1 - r) * hucre_h + hucre_h / 2
                idx += 1
        self._ciz()

    def _zaman_adimi(self, dt):
        if not self.oyun_aktif:
            return
        self.kalan_sure = max(0, self.kalan_sure - 1)
        self.app.refresh_hud(self)
        if self.kalan_sure == 0:
            self._zaman_olay.cancel()
            self.oyun_aktif = False
            self._can_azalt()
            if self.app.canlar > 0 and self.manager.current == self.name:
                self._seviye_yukle()
            return False

    def _ciz(self):
        self.oyun_alani.canvas.clear()
        with self.oyun_alani.canvas:
            for n in self.nesneler:
                x = self.oyun_alani.x + n["x"]
                y = self.oyun_alani.y + n["y"]
                r = (
                    min(
                        self.oyun_alani.width / 3,
                        self.oyun_alani.height / math.ceil(len(self.nesneler) / 3),
                    )
                    * 0.34
                )  # Telefon genisligine gore buyuk sekiller
                if n["bulundu"]:
                    Color(0.18, 0.80, 0.44, 0.72)
                    Ellipse(pos=(x - r - 6, y - r - 6), size=((r + 6) * 2, (r + 6) * 2))
                    continue
                s = n["sekil"]
                renkad = next(
                    (
                        ad
                        for ad, renk in RENK_SOZLUGU.items()
                        if tuple(renk) == tuple(n["renk"])
                    ),
                    "Sari",
                )
                # The shape image is a standalone, antialiased glossy sprite.
                dosya = os.path.join(
                    ASSETS_KLASORU, "sekil_" + s + "_" + renkad + ".png"
                )
                if os.path.isfile(dosya):
                    Color(1, 1, 1, 1)
                    Rectangle(
                        texture=oyun_dokusu("sekil_" + s + "_" + renkad + ".png"),
                        pos=(x - r * 1.17, y - r * 1.17),
                        size=(r * 2.34, r * 2.34),
                    )

    def dokunuldu(self, inst, touch):
        if not getattr(self, "oyun_aktif", False) or not self.oyun_alani.collide_point(
            *touch.pos
        ):
            return
        local_x = touch.x - self.oyun_alani.x
        local_y = touch.y - self.oyun_alani.y

        for n in self.nesneler:
            if n["bulundu"]:
                continue
            if (
                abs(local_x - n["x"]) < self.oyun_alani.width / 6 * 0.9
                and abs(local_y - n["y"])
                < self.oyun_alani.height / math.ceil(len(self.nesneler) / 3) / 2 * 0.9
            ):
                if n["hedef"]:
                    n["bulundu"] = True
                    self.bulunan += 1
                    self.puan += 10
                    self.app.record(self)
                    self.app.effect(touch.x, touch.y, "Harika! +10")
                    ses_efekti_cal("tin")
                    self._ciz()
                    if self.bulunan >= self.hedef_sayi:
                        self._kazandi()
                else:
                    self.app.effect(touch.x, touch.y, "Tekrar dene")
                    self._can_azalt()
                return

    def _kazandi(self):
        self.oyun_aktif = False
        if self._zaman_olay:
            self._zaman_olay.cancel()
        ses_efekti_cal("alkis")
        self.puan += 30
        metni_turkce_seslendir(f"Tebrikler! Seviye {self.seviye}ye geciliyor")
        self.lbl_soru.text = f"TEBRIKLER! Puan: {self.puan}"
        self.app.complete(self, self._seviye_yukle)

    def _can_azalt(self):
        ses_efekti_cal("uzuntu")
        self.app.canlar = max(0, self.app.canlar - 1)
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            if self._zaman_olay:
                self._zaman_olay.cancel()
            can_bitti_popup_goster(self.app, "sekil", self.menuye_don)
        else:
            self._ciz()


# ==========================================
# OYUN 4: HAYVAN KARTI EŞLEŞTİRME (Süper Bulmaca)
# ==========================================
class BulmacaOyunuEkrani(Screen):
    SEMBOLLER = [
        "Aslan",
        "Panda",
        "Kurbaga",
        "Tilki",
        "Fil",
        "Maymun",
        "Zurafa",
        "Penguen",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = OyunArkaplani("memory.jpg")
        self.dis = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(5))

        self.lbl_durum = Label(
            text="",
            size_hint=(1, None),
            height=dp(58),
            bold=True,
            color=(1, 1, 1, 1),
            outline_width=1,
            outline_color=(0.1, 0.25, 0.15, 1),
        )
        self.cerceve = FloatLayout(size_hint=(1, 0.70))
        self.oyun_alani = StencilView(
            size_hint=(0.98, 0.98), pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.oyun_alani.bind(on_touch_down=self.dokunuldu)
        self.oyun_alani.bind(
            size=lambda *_: self._ciz() if getattr(self, "kartlar", None) else None,
            pos=lambda *_: self._ciz() if getattr(self, "kartlar", None) else None,
        )
        self.cerceve.add_widget(self.oyun_alani)

        self.dis.add_widget(self.lbl_durum)
        self.dis.add_widget(self.cerceve)
        self.kok.add_widget(self.dis)
        self.add_widget(self.kok)
        self.ust_panel = None
        self._ezber_olay = None
        self._kapat_olay = None
        self.kartlar = []

    def _panel_kur(self):
        if self.ust_panel is None:
            self.ust_panel = UstPanel(self.app, self.menuye_don)
            self.dis.add_widget(self.ust_panel, index=len(self.dis.children))

    def menuye_don(self):
        self.oyun_aktif = False
        if self._ezber_olay:
            self._ezber_olay.cancel()
        if self._kapat_olay:
            self._kapat_olay.cancel()
            self._kapat_olay = None
        self.manager.current = "menu"

    def oyunu_baslat(self):
        self.app = App.get_running_app()
        self._panel_kur()
        self.seviye = 1
        self.puan = 0
        muzik_ses_seviyesi_ayarla(0.2)
        self._seviye_yukle()

    def _seviye_yukle(self):
        if self._kapat_olay:
            self._kapat_olay.cancel()
            self._kapat_olay = None
        self.oyun_aktif = True
        self.secilenler = []
        self.eslesen_cift = 0
        self.tiklama_kilitli = False
        self.ezber_suresi = 5
        self.tiklama_kilitli = True

        toplam_cift = min(8, 4 + (self.seviye - 1) * 2)
        secilen = random.sample(self.SEMBOLLER, toplam_cift)
        liste = secilen * 2
        random.shuffle(liste)
        self.toplam_cift = toplam_cift
        self.kartlar = [{"sembol": s, "acik": True, "eslesdi": False} for s in liste]

        self.lbl_durum.text = (
            f"Aynı hayvanları bul!  |  Seviye {self.seviye}  |  Puan {self.puan}"
        )
        Clock.schedule_once(lambda dt: self._ciz(), 0)
        metni_turkce_seslendir("Ayni hayvanlari bul")
        if self._ezber_olay:
            self._ezber_olay.cancel()
        self._ezber_olay = Clock.schedule_interval(self._ezber_adimi, 1)

    def _ezber_adimi(self, dt):
        if not self.oyun_aktif:
            return False
        if self.ezber_suresi > 1:
            self.ezber_suresi -= 1
            self._ciz()
        else:
            for k in self.kartlar:
                k["acik"] = False
            self.tiklama_kilitli = False
            ses_efekti_cal("tin")
            self._ciz()
            return False

    def _kart_konumu(self, idx):
        w = self.oyun_alani.width or 340
        h = self.oyun_alani.height or 430
        cols = 4
        rows = math.ceil(len(self.kartlar) / cols)
        gap = max(5, w * 0.018)
        cw = min((w - gap * (cols + 1)) / cols, h * 0.20)
        ch = min(cw * 1.13, (h - gap * (rows + 1)) / rows)
        total_w = cols * cw + (cols - 1) * gap
        total_h = rows * ch + (rows - 1) * gap
        x = (w - total_w) / 2 + (idx % cols) * (cw + gap)
        y = (h + total_h) / 2 - ch - (idx // cols) * (ch + gap)
        return x, y, cw, ch

    def _ciz(self):
        self.oyun_alani.canvas.clear()
        self._kart_etiketleri = getattr(self, "_kart_etiketleri", [])
        for lbl in self._kart_etiketleri:
            if lbl.parent:
                self.oyun_alani.remove_widget(lbl)
        self._kart_etiketleri = []
        sembol_dosyalari = {
            "Aslan": "kart_Aslan.png",
            "Panda": "kart_Panda.png",
            "Kurbaga": "kart_Kurbaga.png",
            "Tilki": "kart_Tilki.png",
            "Fil": "kart_Fil.png",
            "Maymun": "kart_Maymun.png",
            "Zurafa": "kart_Zurafa.png",
            "Penguen": "kart_Penguen.png",
        }
        with self.oyun_alani.canvas:
            for idx, kart in enumerate(self.kartlar):
                x, y, cw, ch = self._kart_konumu(idx)
                ax, ay = self.oyun_alani.x + x, self.oyun_alani.y + y
                if kart["eslesdi"] or kart["acik"]:
                    Color(1, 0.98, 0.88, 1)
                    RoundedRectangle(pos=(ax, ay), size=(cw, ch), radius=[cw * 0.12])
                    Color(1, 1, 1, 1)
                    tex = oyun_dokusu(sembol_dosyalari[kart["sembol"]])
                    side = min(cw, ch) * 0.90
                    Rectangle(
                        texture=tex,
                        pos=(ax + (cw - side) / 2, ay + (ch - side) / 2),
                        size=(side, side),
                    )
                    if kart["eslesdi"]:
                        Color(0.2, 1, 0.4, 1)
                        Line(
                            rounded_rectangle=(ax + 2, ay + 2, cw - 4, ch - 4, 8),
                            width=3,
                        )
                else:
                    Color(1, 1, 1, 1)
                    Rectangle(
                        texture=oyun_dokusu("card.png"), pos=(ax, ay), size=(cw, ch)
                    )
        for lbl in self._kart_etiketleri:
            self.oyun_alani.add_widget(lbl)

    def dokunuldu(self, inst, touch):
        if (
            not getattr(self, "oyun_aktif", False)
            or self.tiklama_kilitli
            or not self.oyun_alani.collide_point(*touch.pos)
        ):
            return
        local_x = touch.x - self.oyun_alani.x
        local_y = touch.y - self.oyun_alani.y

        for idx, kart in enumerate(self.kartlar):
            if kart["acik"] or kart["eslesdi"]:
                continue
            x, y, cw, ch = self._kart_konumu(idx)
            if x <= local_x <= x + cw and y <= local_y <= y + ch:
                ses_efekti_cal("tik")
                kart["acik"] = True
                self.secilenler.append(kart)
                self._ciz()
                if len(self.secilenler) == 2:
                    self.tiklama_kilitli = True
                    k1, k2 = self.secilenler
                    if k1["sembol"] == k2["sembol"]:
                        ses_efekti_cal("alkis")
                        k1["eslesdi"] = True
                        k2["eslesdi"] = True
                        self.eslesen_cift += 1
                        self.puan += 15
                        self.app.record(self)
                        self.secilenler = []
                        self.tiklama_kilitli = False
                        self._ciz()
                        if self.eslesen_cift >= self.toplam_cift:
                            self._kazandi()
                    else:
                        ses_efekti_cal("uzuntu")
                        self._kapat_olay = Clock.schedule_once(
                            lambda dt, c1=k1, c2=k2: self._kapat(c1, c2), 0.7
                        )
                return

    def _kapat(self, k1, k2):
        self._kapat_olay = None
        if not getattr(self, "oyun_aktif", False):
            return
        k1["acik"] = False
        k2["acik"] = False
        self.secilenler = []
        self.tiklama_kilitli = False
        self._can_azalt()
        if self.oyun_aktif:
            self._ciz()

    def _kazandi(self):
        self.oyun_aktif = False
        ses_efekti_cal("alkis")
        self.puan += 40
        metni_turkce_seslendir(f"Tebrikler! Seviye {self.seviye}ye geciliyor")
        self.lbl_durum.text = f"TEBRIKLER! Puan: {self.puan}"
        self.app.complete(self, self._seviye_yukle)

    def _can_azalt(self):
        self.app.canlar = max(0, self.app.canlar - 1)
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            can_bitti_popup_goster(self.app, "bulmaca", self.menuye_don)


# ==========================================
# ANA UYGULAMA (Gerçek Saniye Sayaç Düzeltmesi ile)
# ==========================================
# Revised shared lifecycle and UI. Existing shape, balloon and card rules above retained.
from interface import Login, Menu, Settings, Achievements, button, label, dialog, cream

TR = {
    "Kirmizi": "Kırmızı",
    "Yesil": "Yeşil",
    "Mavi": "Mavi",
    "Sari": "Sarı",
    "Mor": "Mor",
    "Turuncu": "Turuncu",
    "Yuvarlak": "Daire",
    "Kare": "Kare",
    "Ucgen": "Üçgen",
    "Yildiz": "Yıldız",
}


class UstPanel(BoxLayout):
    def __init__(self, app, geri_callback, **kw):
        super().__init__(size_hint_y=None, height=dp(64), spacing=dp(5), **kw)
        self.app = app
        cream(self)
        self.add_widget(button("Menü", geri_callback, size_hint_x=0.9))
        self.kalp_gosterge = KalpGostergesi(3, 3)
        self.add_widget(self.kalp_gosterge)
        self.lbl_sure = label("")
        self.lbl_sure.size_hint_x = 0.7
        self.lbl_sure.font_size = "13sp"
        self.add_widget(self.lbl_sure)
        pause = button("Duraklat", app.pause_game, size_hint_x=1.25)
        pause.font_size = "15sp"
        self.add_widget(pause)

    def ses_guncelle(self):
        self.kalp_gosterge.guncelle(self.app.canlar, 3)


class OyunArkaplani(FloatLayout):
    def __init__(self, dosya, **kw):
        super().__init__(**kw)
        source = dosya
        self.add_widget(
            Image(source=os.path.join(ASSETS_KLASORU, source), fit_mode="cover")
        )


# Rewarded advertisements are optional; waiting always remains available.
def can_bitti_popup_goster(app, oyun_kodu, menuye_don_callback):
    screen = app.sm.get_screen(oyun_kodu)
    screen.oyun_aktif = False
    app.record(screen)
    app.show_lives_dialog(oyun_kodu, menuye_don_callback)


class MinikKasiflerApp(App):
    def build(self):
        mark("app-build")
        global SES_ACIK
        LabelBase.register(
            name="Roboto",
            fn_regular=os.path.join(ASSETS_KLASORU, "DejaVuSans.ttf"),
            fn_bold=os.path.join(ASSETS_KLASORU, "DejaVuSans-Bold.ttf"),
        )
        Window.clearcolor = (0.57, 0.83, 0.96, 1)
        Window.softinput_mode = "below_target"
        self.kayit = SaveStore(self.user_data_dir)
        mark("storage-ready")
        SES_ACIK = self.kayit.data["sound"]
        self.max_can = 3
        self._canlar = self.kayit.data["lives"]
        self._next_life_at = self.kayit.data["next_life_at"]
        self._sync_lives()
        self.modal = None
        self.rewarded = RewardedAds()
        self._life_wait_event = None
        self._life_wait_deadline = None
        self._life_game = None
        self.effects = []
        self.sm = ScreenManager(
            transition=__import__(
                "kivy.uix.screenmanager", fromlist=["NoTransition"]
            ).NoTransition()
        )
        mark("create-screens")
        for screen in (
            Login(name="giris"),
            Menu(name="menu"),
            Settings(name="settings"),
            Achievements(name="achievements"),
            BalonOyunuEkrani(name="balon"),
            AriOyunuEkrani(name="ari"),
            SekilOyunuEkrani(name="sekil"),
            BulmacaOyunuEkrani(name="bulmaca"),
        ):
            self.sm.add_widget(screen)
            for attr in ("lbl_skor", "lbl_soru", "lbl_durum"):
                indicator = getattr(screen, attr, None)
                if indicator is not None:
                    if attr != "lbl_soru":
                        cream(indicator)
                    indicator.color = (0.13, 0.18, 0.29, 1)
                    indicator.outline_width = 0
            for widget in screen.walk():
                if isinstance(widget, Label):
                    if not getattr(widget, "_relief", None):
                        widget.font_size *= 1.10
                    widget.halign = "center"
                    widget.valign = "middle"
                    widget.bind(size=lambda w, v: setattr(w, "text_size", (v[0] - dp(12), v[1]) if isinstance(w, Button) else (v[0], None)))
        self.sm.bind(current=self.changed_screen)
        Window.bind(on_keyboard=self.back_key)
        self.heartbeat = Clock.schedule_interval(self.tick, 1 / 30)
        self.life_heartbeat = Clock.schedule_interval(lambda dt: self._sync_lives(), 1)
        Clock.schedule_once(lambda dt: self.rewarded.initialize(), 0)
        self.ad_heartbeat = Clock.schedule_interval(self.check_reward, 0.35)
        Clock.schedule_once(lambda dt: self.apply_audio(), 0)
        mark("ui-built")
        return self.sm

    @property
    def canlar(self):
        self._sync_lives()
        return self._canlar

    @canlar.setter
    def canlar(self, value):
        self._sync_lives()
        old = self._canlar
        self._canlar = max(0, min(self.max_can, int(value)))
        if self._canlar == self.max_can:
            self._next_life_at = None
        elif self._canlar < old and self._next_life_at is None:
            self._next_life_at = time.time() + 90
        elif self._canlar < old and self._next_life_at is not None:
            pass  # Keep the existing recovery clock running.
        elif self._canlar > old and self._next_life_at is None:
            self._next_life_at = time.time() + 90
        self._save_lives()

    def _save_lives(self):
        self.kayit.data["lives"] = self._canlar
        self.kayit.data["next_life_at"] = self._next_life_at
        self.kayit.save()

    def _sync_lives(self):
        if self._canlar >= self.max_can:
            if self._next_life_at is not None:
                self._next_life_at = None
                self._save_lives()
            return
        if self._next_life_at is None:
            self._next_life_at = time.time() + 90
            self._save_lives()
            return
        now = time.time()
        if now < self._next_life_at:
            return
        earned = int((now - self._next_life_at) // 90) + 1
        self._canlar = min(self.max_can, self._canlar + earned)
        if self._canlar >= self.max_can:
            self._next_life_at = None
        else:
            self._next_life_at += earned * 90
        self._save_lives()
        for code in ("balon", "ari", "sekil", "bulmaca"):
            if hasattr(self, "sm") and self.sm.has_screen(code):
                panel = getattr(self.sm.get_screen(code), "ust_panel", None)
                if panel:
                    panel.kalp_gosterge.guncelle(self._canlar, self.max_can)

    def cancel_life_wait(self):
        if self._life_wait_event:
            self._life_wait_event.cancel()
            self._life_wait_event = None
        self._life_game = None
        self._life_wait_label = None

    def show_lives_dialog(self, code, back_callback):
        self._sync_lives()
        self._life_game = code
        if self._life_wait_event is None:
            self._life_wait_event = Clock.schedule_interval(self.update_life_wait, 1)
        self.render_life_dialog()

    def render_life_dialog(self):
        if not self._life_game:
            return
        if self.canlar > 0:
            self._resume_after_life()
            return
        screen = self.sm.get_screen(self._life_game)
        remaining = max(0, int(math.ceil((self._next_life_at or time.time()) - time.time())))
        if self.modal:
            self.modal.dismiss(animation=False)
            self.modal = None
        self.modal = dialog(
            "Canların Bitti",
            f"Puan: {getattr(screen, 'puan', 0)} | Seviye: {getattr(screen, 'seviye', 1)}\n"
            f"Reklam izle, 1 can kazan.\nYa da {remaining} saniye bekle.",
            [("Reklam İzle (+1 Can)", self.watch_life_ad),
             ("Bekle", self.wait_life),
             ("Ana Menü", self.leave_life_screen)],
        )
        # Keep the modal intact and update only its text every second.
        from kivy.uix.label import Label as KivyLabel
        for w in self.modal.walk():
            if isinstance(w, KivyLabel) and "saniye bekle" in w.text:
                self._life_wait_label = w
                break

    def wait_life(self):
        self.render_life_dialog()

    def update_life_wait(self, dt):
        self._sync_lives()
        if not self._life_game:
            return False
        if self._canlar > 0:
            self._resume_after_life()
            return False
        remaining = max(0, int(math.ceil((self._next_life_at or time.time()) - time.time())))
        w = getattr(self, "_life_wait_label", None)
        if w is not None:
            screen = self.sm.get_screen(self._life_game)
            w.text = (f"Puan: {getattr(screen, 'puan', 0)} | "
                      f"Seviye: {getattr(screen, 'seviye', 1)}\n"
                      f"Reklam izle, 1 can kazan.\nYa da {remaining} saniye bekle.")

    def _resume_after_life(self):
        code = self._life_game
        self.cancel_life_wait()
        if self.modal:
            self.modal.dismiss(animation=False)
            self.modal = None
        if not code or self.sm.current != code:
            return
        s = self.sm.get_screen(code)
        s._timeout = 90
        if s.name in ("sekil", "bulmaca"):
            s._seviye_yukle()
        else:
            s.oyun_aktif = True
            if s._olay:
                s._olay.cancel()
            s._olay = Clock.schedule_interval(s.adim, 1 / 30)
        s.ust_panel.ses_guncelle()
        self.refresh_hud(s)

    def watch_life_ad(self):
        if not self._life_game:
            return
        if not self.rewarded.show():
            self.render_life_dialog()
            if self.modal:
                self.modal.dismiss(animation=False)
            self.modal = dialog("Reklam Hazır Değil", "Şu an reklam bulunamadı.\n90 saniyelik bekleme devam ediyor.",
                                [("Beklemeye Dön", self.render_life_dialog),
                                 ("Ana Menü", self.leave_life_screen)])

    def check_reward(self, dt):
        status = self.rewarded.poll()
        if status == 'earned' and self._life_game:
            self.grant_life()
        elif status in ('closed', 'failed') and self._life_game:
            self.render_life_dialog()

    def grant_life(self):
        if not self._life_game:
            return
        self.canlar = min(self.max_can, self.canlar + 1)
        self._resume_after_life()

    def leave_life_screen(self):
        self.cancel_life_wait()
        self.sm.current = 'menu'

    def apply_audio(self):
        global SES_ACIK
        SES_ACIK = self.kayit.data["sound"]
        if self.kayit.data["music"]:
            muzik_baslat()
        elif _MUZIK:
            _MUZIK.stop()
        if not SES_ACIK:
            for sound in _SES_CACHE.values():
                sound.stop()

    def start_game(self, code):
        if self.modal:
            self.modal.dismiss()
            self.modal = None
        if self.canlar <= 0:
            self.show_lives_dialog(code, lambda: self.leave_life_screen())
            return
        self.stop_games()
        s = self.sm.get_screen(code)
        s._completed = 0
        s._last_completed_level = 0
        s.elapsed_time = 0
        s._timeout = 90
        self.sm.current = code
        s.oyunu_baslat()
        s.ust_panel.ses_guncelle()
        self.refresh_hud(s)

    def stop_games(self):
        self.clear_effects()
        for code in ("balon", "ari", "sekil", "bulmaca"):
            s = self.sm.get_screen(code)
            if hasattr(s, "puan"):
                self.record(s)
            s.oyun_aktif = False
            for attr in ("_olay", "_zaman_olay", "_kapat_olay", "_ezber_olay"):
                ev = getattr(s, attr, None)
                if ev:
                    ev.cancel()
                    setattr(s, attr, None)

    def changed_screen(self, sm, name):
        self.clear_effects()
        # Any route out of a game invalidates its timers, including Android Back.
        for code in ("balon", "ari", "sekil", "bulmaca"):
            if code == name:
                continue
            s = sm.get_screen(code)
            if hasattr(s, "puan"):
                self.record(s)
            s.oyun_aktif = False
            for attr in ("_olay", "_zaman_olay", "_kapat_olay", "_ezber_olay"):
                ev = getattr(s, attr, None)
                if ev:
                    ev.cancel()
                    setattr(s, attr, None)

    def record(self, s):
        self.kayit.record(s.name, s.puan)
        self.refresh_hud(s)

    def complete(self, s, continuation):
        if not s.oyun_aktif and s.name not in ("sekil", "bulmaca"):
            return
        if getattr(s, "_last_completed_level", 0) >= s.seviye:
            return
        s._last_completed_level = s.seviye
        s.oyun_aktif = False
        stars = max(1, min(3, self.canlar))
        self.kayit.record(s.name, s.puan, s.seviye, True, stars)
        level = s.seviye
        s._completed += 1

        def next_level():
            s.seviye = level + 1
            s._timeout = 90
            s.oyun_aktif = True
            if s.name == "balon":
                s.balonlar = []
            continuation()
            self.refresh_hud(s)

        self.modal = dialog(
            "Seviye Tamamlandı",
            f"Tebrikler!\nSeviye: {level}\nPuan: {s.puan}\nYıldız: {stars}/3",
            [
                ("Devam Et", next_level),
                ("Tekrar Oyna", lambda: self.start_game(s.name)),
                ("Ana Menü", lambda: setattr(self.sm, "current", "menu")),
            ],
            stars=stars,
        )

    def tick(self, dt):
        if self.sm.current not in ("balon", "ari", "sekil", "bulmaca"):
            return
        s = self.sm.current_screen
        if not getattr(s, "oyun_aktif", False):
            return
        s.elapsed_time += dt
        # Shape game has its own timer; others have a level time limit.
        if s.name != "sekil":
            s._timeout -= dt
            if s._timeout <= 0:
                s._timeout = 90
                s._can_azalt()
        self.refresh_hud(s)

    def refresh_hud(self, s):
        if s.name == "bulmaca":
            s.lbl_durum.text = (
                f"Puan: {s.puan} | Seviye: {s.seviye}\nEşleşen: {s.eslesen_cift}/{s.toplam_cift} çift"
            )
        elif s.name == "sekil":
            s.lbl_durum.text = (
                f"Puan: {s.puan} | Seviye: {s.seviye} | Bulunan: {s.bulunan}/{s.hedef_sayi}"
            )
        if s.name == "balon":
            s.lbl_skor.text = f"Puan: {s.puan} | Seviye: {s.seviye}\nBalonları patlat • Üzgün balona dokunma"
        if s.ust_panel:
            remaining = s.kalan_sure if s.name == "sekil" else s._timeout
            s.ust_panel.lbl_sure.text = "Süre\n" + format_sure(remaining)

    def pause_game(self):
        if self.sm.current not in ("balon", "ari", "sekil", "bulmaca"):
            return
        s = self.sm.current_screen
        if not getattr(s, "oyun_aktif", False):
            return
        s.oyun_aktif = False
        # Pending mismatch is closed immediately. Its scheduled callback is cancelled.
        ev = getattr(s, "_kapat_olay", None)
        if ev:
            ev.cancel()
            s._kapat_olay = None
            for card in s.secilenler:
                card["acik"] = False
            s.secilenler = []
            s.tiklama_kilitli = False
            s._ciz()
        self.modal = dialog(
            "Duraklatıldı",
            "Hazır olduğunda devam edebilirsin.",
            [
                ("Devam Et", lambda: setattr(s, "oyun_aktif", True)),
                ("Tekrar Oyna", lambda: self.start_game(s.name)),
                ("Ana Menü", lambda: setattr(self.sm, "current", "menu")),
            ],
        )

    def finish_effect(self, widget):
        if widget in self.effects:
            self.effects.remove(widget)
        if widget in Window.children:
            Window.remove_widget(widget)

    def clear_effects(self):
        from kivy.animation import Animation

        for widget in self.effects[:]:
            Animation.cancel_all(widget)
            self.finish_effect(widget)

    def effect(self, x, y, text):
        from kivy.animation import Animation

        l = Label(
            text=text,
            bold=True,
            font_size="23sp",
            color=(1, 0.92, 0.12, 1),
            outline_width=2,
            outline_color=(0.1, 0.2, 0.1, 1),
            size_hint=(None, None),
            size=(dp(180), dp(60)),
            pos=(x - dp(90), y),
        )
        Window.add_widget(l)
        self.effects.append(l)
        if "+" in text or "Harika" in text:
            for i in range(5):
                particle = Image(
                    source=os.path.join(ASSETS_KLASORU, "sekil_Yildiz_Sari.png"),
                    size_hint=(None, None),
                    size=(dp(26), dp(26)),
                    pos=(x, y),
                )
                Window.add_widget(particle)
                self.effects.append(particle)
                angle = i * math.tau / 5
                anim = Animation(
                    x=x + math.cos(angle) * dp(65),
                    y=y + math.sin(angle) * dp(65),
                    opacity=0,
                    duration=0.45,
                )
                anim.bind(
                    on_complete=lambda animation, widget: self.finish_effect(widget)
                )
                anim.start(particle)
        a = Animation(y=y + dp(45), opacity=0, duration=0.55)
        a.bind(on_complete=lambda *_: self.finish_effect(l))
        a.start(l)

    def confirm_exit(self):
        if self.modal:
            self.modal.dismiss()
            self.modal = None
        self.modal = dialog(
            "Oyundan Çık",
            "Oyundan çıkmak istiyor musun?",
            [
                ("Oyuna Dön", lambda: None),
                ("Çıkış", self.stop),
            ],
        )

    def back_key(self, window, key, *_):
        if key != 27:
            return False
        if self.sm.current in ("balon", "ari", "sekil", "bulmaca"):
            self.pause_game()
        elif self.sm.current in ("menu", "giris"):
            self.confirm_exit()
        else:
            self.sm.current = "menu"
        return True

    def on_pause(self):
        self.sm.get_screen("menu").stop_animation()
        self.pause_game()
        if _MUZIK:
            _MUZIK.stop()
        self.kayit.save()
        return True

    def on_resume(self):
        self._sync_lives()
        if self.sm.current == "menu":
            self.sm.get_screen("menu").start_animation()
        self.apply_audio()

    def on_stop(self):
        self.sm.get_screen("menu").stop_animation()
        self.stop_games()
        self.heartbeat.cancel()
        self.life_heartbeat.cancel()
        self.ad_heartbeat.cancel()
        self.cancel_life_wait()
        self.kayit.save()
        if _MUZIK:
            _MUZIK.stop()


if __name__ == "__main__":
    mark("app-run")
    MinikKasiflerApp().run()
