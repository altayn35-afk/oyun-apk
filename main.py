# -*- coding: utf-8 -*-
"""
MINIK KASIFLER ATOLYESI - KIVY SURUMU (TAM)
Android'e derlenebilir hale getirmek icin pygame yerine Kivy'nin kendi
ses motoru (SoundLoader) kullanildi - bu, buildozer derlemesindeki
'longintrepr.h' hatasinin kaynagi olan pygame bagimliligini tamamen kaldirir.

Masaustunde test icin:
    pip install kivy --break-system-packages
    python3 main.py
"""

import math
import os
import random
import threading
import time

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle, Triangle, Line
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window

try:
    from gtts import gTTS
    GTTS_MEVCUT = True
except ImportError:
    GTTS_MEVCUT = False

ASSETS_KLASORU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ==========================================
# SES YONETIMI (Kivy SoundLoader - pygame YOK)
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
    if not SES_ACIK:
        return
    dosya = _ses_dosyasi("fon_muzigi.mp3")
    if not dosya:
        # kok klasorde de arayalim (kullanici kendi mp3'unu koymus olabilir)
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
    if _MUZIK and SES_ACIK:
        try:
            _MUZIK.volume = seviye
        except Exception:
            pass


def genel_ses_ac_kapa():
    global SES_ACIK
    SES_ACIK = not SES_ACIK
    if not SES_ACIK:
        if _MUZIK:
            _MUZIK.stop()
    else:
        muzik_baslat()
    return SES_ACIK


def metni_turkce_seslendir(metin, bitince_bunu_yap=None):
    if not SES_ACIK or not GTTS_MEVCUT:
        if bitince_bunu_yap:
            Clock.schedule_once(lambda dt: bitince_bunu_yap(), 0)
        return

    def seslendir():
        dosya_adi = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"gecici_ses_{random.randint(1000, 9999)}.mp3")
        try:
            tts = gTTS(text=metin, lang='tr', slow=False)
            tts.save(dosya_adi)
            s = SoundLoader.load(dosya_adi)
            if s and SES_ACIK:
                s.play()
                time.sleep(s.length if s.length else 1.5)
            try:
                os.remove(dosya_adi)
            except Exception:
                pass
        except Exception as e:
            print(f"Turkce seslendirme hatasi: {e}")
        if bitince_bunu_yap:
            Clock.schedule_once(lambda dt: bitince_bunu_yap(), 0)

    threading.Thread(target=seslendir, daemon=True).start()


# ==========================================
# ORTAK RENKLER / YARDIMCILAR
# ==========================================
BALON_RENKLERI = [
    (1, 0.30, 0.30, 1), (0.30, 0.58, 1, 1), (0.30, 1, 0.53, 1),
    (1, 0.84, 0.20, 1), (0.70, 0.40, 1, 1), (1, 0.60, 0.20, 1),
]

RENK_SOZLUGU = {
    "Kirmizi": (1, 0.2, 0.2, 1), "Yesil": (0.18, 0.80, 0.44, 1),
    "Mavi": (0.20, 0.60, 0.86, 1), "Turuncu": (0.90, 0.49, 0.13, 1),
    "Mor": (0.61, 0.35, 0.71, 1), "Sari": (0.95, 0.77, 0.06, 1),
}
SEKIL_TIPLERI = ["Yuvarlak", "Kare", "Ucgen", "Yildiz"]


def hex_karistir(renk, katsayi=1.0):
    r, g, b, a = renk
    return (min(1, r * katsayi), min(1, g * katsayi), min(1, b * katsayi), a)


class RenkliArkaplan(FloatLayout):
    def __init__(self, renk=(0.44, 0.84, 1, 1), **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*renk)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._g, pos=self._g)

    def _g(self, *a):
        self.rect.size = self.size
        self.rect.pos = self.pos


def can_kalpleri_metni(canlar, maxcan):
    return ("<3 " * canlar) + ("X " * (maxcan - canlar))


# ==========================================
# UST PANEL: CAN + SES BUTONU (tum oyun ekranlarinda ortak)
# ==========================================
class UstPanel(BoxLayout):
    def __init__(self, app, geri_callback, **kwargs):
        super().__init__(orientation="horizontal", size_hint=(1, None), height=50,
                          padding=8, spacing=8, **kwargs)
        self.app = app

        self.btn_geri = Button(text="< Menu", size_hint=(0.2, 1),
                                background_color=(0.90, 0.30, 0.30, 1), bold=True)
        self.btn_geri.bind(on_release=lambda *a: geri_callback())
        self.add_widget(self.btn_geri)

        self.lbl_can = Label(text=can_kalpleri_metni(app.canlar, app.max_can),
                              size_hint=(0.5, 1), color=(0.83, 0.18, 0.18, 1), bold=True)
        self.add_widget(self.lbl_can)

        self.btn_ses = Button(text="Ses Acik" if SES_ACIK else "Ses Kapali",
                               size_hint=(0.3, 1),
                               background_color=(0.18, 0.80, 0.44, 1) if SES_ACIK else (0.90, 0.30, 0.30, 1))
        self.btn_ses.bind(on_release=self.ses_degistir)
        self.add_widget(self.btn_ses)

    def ses_guncelle(self):
        self.lbl_can.text = can_kalpleri_metni(self.app.canlar, self.app.max_can)

    def ses_degistir(self, *a):
        acik = genel_ses_ac_kapa()
        self.btn_ses.text = "Ses Acik" if acik else "Ses Kapali"
        self.btn_ses.background_color = (0.18, 0.80, 0.44, 1) if acik else (0.90, 0.30, 0.30, 1)


# ==========================================
# CAN BITTI POPUP
# ==========================================
def can_bitti_popup_goster(app, oyun_kodu, tekrar_baslat_callback, menuye_don_callback):
    mesajlar = {
        "balon": ("Eyvah, Balonlar Gokyuzune Kacti!", "SIHIRLI IGNE ICIN +1 CAN"),
        "ari": ("Sevimli Ari Yorgun Dustu!", "ARIYI KURTARMAK ICIN +1 CAN"),
        "sekil": ("Tum Ipuclari Saklandi!", "SUPER BUYUTEC ICIN +1 CAN"),
        "bulmaca": ("Sihirli Kule Bloklari Bitti!", "KULEYI BUYUTMEK ICIN +1 CAN"),
    }
    alt_metin, buton_metni = mesajlar.get(oyun_kodu, ("Macera Yarida Kaldi!", "+1 CAN KAZAN"))

    icerik = BoxLayout(orientation="vertical", spacing=10, padding=10)
    icerik.add_widget(Label(text="CANLARIN BITTI!", font_size="22sp", bold=True,
                             color=(1, 0.3, 0.3, 1), size_hint=(1, 0.3)))
    icerik.add_widget(Label(text=alt_metin, font_size="14sp", color=(1, 0.9, 0.4, 1), size_hint=(1, 0.2)))

    popup = Popup(title="", separator_height=0, size_hint=(0.85, 0.55), auto_dismiss=False)

    def can_kazan(*a):
        app.canlar = min(app.max_can, app.canlar + 1)
        ses_efekti_cal("alkis")
        popup.dismiss()
        menuye_don_callback()

    def menuye_git(*a):
        popup.dismiss()
        menuye_don_callback()

    btn_reklam = Button(text=buton_metni, size_hint=(1, 0.25),
                         background_color=(0.18, 0.80, 0.44, 1), bold=True)
    btn_reklam.bind(on_release=can_kazan)
    icerik.add_widget(btn_reklam)

    btn_menu = Button(text="Menuye Don", size_hint=(1, 0.25),
                       background_color=(0.90, 0.30, 0.30, 1))
    btn_menu.bind(on_release=menuye_git)
    icerik.add_widget(btn_menu)

    popup.content = icerik
    popup.open()


# ==========================================
# EKRAN 1: GIRIS EKRANI
# ==========================================
class GirisEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kok = RenkliArkaplan(renk=(0.17, 0.12, 0.23, 1))

        icerik = BoxLayout(orientation="vertical", padding=40, spacing=18,
                            size_hint=(0.85, 0.55),
                            pos_hint={"center_x": 0.5, "center_y": 0.5})

        icerik.add_widget(Label(text="MINIK KASIFLER ATOLYESI", font_size="26sp", bold=True,
                                 color=(1, 0.84, 0.2, 1), size_hint=(1, 0.3)))
        icerik.add_widget(Label(text="Eglenceli Ogrenme Dunyasina Hos Geldin!",
                                 font_size="15sp", color=(0.3, 1, 1, 1), size_hint=(1, 0.15)))

        self.isim_kutusu = TextInput(hint_text="Adin Nedir Minik Kasif?", multiline=False,
                                      font_size="18sp", size_hint=(1, 0.18), halign="center",
                                      padding_y=(15, 15))
        icerik.add_widget(self.isim_kutusu)

        btn_basla = Button(text="MACERAYA BASLA", font_size="18sp", bold=True,
                            background_color=(1, 0.30, 0.10, 1), size_hint=(1, 0.2))
        btn_basla.bind(on_release=self.oyuna_basla)
        icerik.add_widget(btn_basla)

        kok.add_widget(icerik)
        self.add_widget(kok)

    def oyuna_basla(self, *a):
        app = App.get_running_app()
        isim = self.isim_kutusu.text.strip()
        if isim:
            app.cocuk_ismi = isim
        ses_efekti_cal("tin")
        menu = self.manager.get_screen("menu")
        menu.guncelle()
        self.manager.current = "menu"


# ==========================================
# EKRAN 2: MENU
# ==========================================
class MenuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kok = RenkliArkaplan(renk=(0.11, 0.16, 0.13, 1))
        self.dis = BoxLayout(orientation="vertical", padding=25, spacing=12)

        self.baslik = Label(text="Oyununu Sec!", font_size="20sp", bold=True,
                             color=(0.55, 0.90, 0.60, 1), size_hint=(1, 0.12))
        self.dis.add_widget(self.baslik)

        self.can_label = Label(text="", font_size="14sp", color=(1, 0.5, 0.5, 1), size_hint=(1, 0.08))
        self.dis.add_widget(self.can_label)

        oyunlar = [
            ("Balon Patlatma Macerasi", (1, 0.30, 0.10, 1), "balon"),
            ("Bal Pesinde Neseli Ari", (1, 0.70, 0.10, 1), "ari"),
            ("Sekil ve Renk Avcisi", (0.18, 0.55, 0.34, 1), "sekil"),
            ("Surpriz Bulmaca Kulesi", (0.83, 0.33, 0.0, 1), "bulmaca"),
        ]
        for metin, renk, kod in oyunlar:
            btn = Button(text=metin, font_size="16sp", bold=True, background_color=renk,
                         size_hint=(1, 0.15))
            btn.bind(on_release=lambda inst, k=kod: self.oyun_sec(k))
            self.dis.add_widget(btn)

        btn_isim = Button(text="Isim Degistir", font_size="12sp",
                           background_color=(0.16, 0.5, 0.73, 1), size_hint=(1, 0.09))
        btn_isim.bind(on_release=lambda *a: setattr(self.manager, "current", "giris"))
        self.dis.add_widget(btn_isim)

        self.kok.add_widget(self.dis)
        self.add_widget(self.kok)

    def guncelle(self):
        app = App.get_running_app()
        self.baslik.text = f"Sevgili {app.cocuk_ismi}, Oyununu Sec!"
        self.can_label.text = f"Can: {can_kalpleri_metni(app.canlar, app.max_can)}"

    def on_enter(self):
        self.guncelle()
        muzik_ses_seviyesi_ayarla(0.5)

    def oyun_sec(self, kod):
        app = App.get_running_app()
        ses_efekti_cal("tin")
        if app.canlar <= 0:
            can_bitti_popup_goster(app, kod, None, lambda: setattr(self.manager, "current", "menu"))
            return
        self.manager.current = kod
        self.manager.get_screen(kod).oyunu_baslat()


# ==========================================
# OYUN 1: BALON PATLATMA
# ==========================================
class BalonOyunuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = RenkliArkaplan(renk=(0.44, 0.84, 1, 1))
        self.dis = BoxLayout(orientation="vertical")

        self.oyun_alani = Widget()
        self.oyun_alani.bind(on_touch_down=self.dokunuldu)

        self.lbl_skor = Label(text="Puan: 0 | Seviye: 1", size_hint=(1, None), height=30,
                               color=(0.1, 0.35, 0.12, 1), bold=True)

        self.dis.add_widget(self.lbl_skor)
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
        self.oyun_aktif = True
        muzik_ses_seviyesi_ayarla(0.2)
        self.yeni_balon()
        if self._olay:
            self._olay.cancel()
        self._olay = Clock.schedule_interval(self.adim, 1 / 30)

    def yeni_balon(self):
        genislik = self.oyun_alani.width or 400
        self.balon_x = random.uniform(60, max(80, genislik - 60))
        self.balon_y = -20
        self.balon_aci = 0
        self.balon_renk = random.choice(BALON_RENKLERI)

    def adim(self, dt):
        if not self.oyun_aktif:
            return
        h = self.oyun_alani.height or 600
        w = self.oyun_alani.width or 400

        hiz = 2.0 + self.seviye * 0.8
        self.balon_y += hiz
        self.balon_aci += 0.08
        self.balon_x += math.sin(self.balon_aci) * 2
        self.balon_x = max(40, min(w - 40, self.balon_x))

        self.oyun_alani.canvas.clear()
        with self.oyun_alani.canvas:
            r = 34
            Color(*self.balon_renk)
            Ellipse(pos=(self.balon_x - r, self.balon_y - r), size=(r * 2, r * 2))
            Color(1, 1, 1, 0.5)
            Ellipse(pos=(self.balon_x - r * 0.4, self.balon_y + r * 0.2), size=(r * 0.5, r * 0.35))
            Color(0.3, 0.3, 0.3, 1)
            Line(points=[self.balon_x, self.balon_y - r, self.balon_x, self.balon_y - r - 25], width=1.2)

        if self.balon_y > h + 40:
            self.yeni_balon()
            self._can_azalt()

    def dokunuldu(self, inst, touch):
        if not self.oyun_aktif or not self.oyun_alani.collide_point(*touch.pos):
            return
        r = 45
        if abs(touch.x - self.balon_x) < r and abs(touch.y - self.balon_y) < r:
            self.puan += 10
            self.seviye = (self.puan // 30) + 1
            self.lbl_skor.text = f"Puan: {self.puan} | Seviye: {self.seviye}"
            ses_efekti_cal("tin")
            self.yeni_balon()

    def _can_azalt(self):
        self.app.canlar -= 1
        ses_efekti_cal("uzuntu")
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            if self._olay:
                self._olay.cancel()
            can_bitti_popup_goster(self.app, "balon", None, self.menuye_don)


# ==========================================
# OYUN 2: BAL PESINDE ARI
# ==========================================
class AriOyunuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = RenkliArkaplan(renk=(0.44, 0.84, 1, 1))
        self.dis = BoxLayout(orientation="vertical")
        self.oyun_alani = Widget()
        self.oyun_alani.bind(on_touch_move=self.parmak_hareket, on_touch_down=self.parmak_hareket)

        self.lbl_skor = Label(text="Puan: 0 | Seviye: 1", size_hint=(1, None), height=30,
                               color=(0.1, 0.35, 0.12, 1), bold=True)
        self.dis.add_widget(self.lbl_skor)
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
        self.kalan_mesafe = 500
        self.ari_y = 300
        self.ari_dondu = False
        self.engeller = []
        self.bal_kutusu_x = None
        self.oyun_aktif = True
        muzik_ses_seviyesi_ayarla(0.2)
        if self._olay:
            self._olay.cancel()
        self._olay = Clock.schedule_interval(self.adim, 1 / 30)

    def parmak_hareket(self, inst, touch):
        if self.oyun_aktif and not self.ari_dondu and self.oyun_alani.collide_point(*touch.pos):
            self.ari_y = touch.y

    def adim(self, dt):
        if not self.oyun_aktif or self.ari_dondu:
            return
        w = self.oyun_alani.width or 400
        h = self.oyun_alani.height or 600
        ari_x = 90

        hiz = 3.5 + self.seviye * 1.2
        self.kalan_mesafe -= 1

        if self.kalan_mesafe > 60 and random.random() < (0.02 + self.seviye * 0.006):
            self.engeller.append([w + 40, random.uniform(80, h - 80), random.uniform(50, 100)])

        yeni = []
        carpisti = False
        for eng in self.engeller:
            eng[0] -= hiz
            ex, ey, eh = eng
            if abs(ari_x - ex) < 30 and abs(self.ari_y - ey) < (eh / 2 + 20):
                carpisti = True
            if ex > -40:
                yeni.append(eng)
        self.engeller = yeni

        if carpisti:
            self.ari_dondu = True
            ses_efekti_cal("uzuntu")
            Clock.schedule_once(lambda dt2: self._carpma_sonrasi(), 0.6)
            self._ciz(ari_x, h)
            return

        kazanildi = False
        if self.kalan_mesafe <= 0:
            if self.bal_kutusu_x is None:
                self.bal_kutusu_x = w + 40
            self.bal_kutusu_x -= hiz
            if abs(ari_x - self.bal_kutusu_x) < 45 and abs(self.ari_y - h / 2) < 60:
                kazanildi = True

        self._ciz(ari_x, h)

        if kazanildi:
            ses_efekti_cal("tin")
            self.seviye += 1
            self.puan += 50
            self.kalan_mesafe = 500 + self.seviye * 150
            self.bal_kutusu_x = None
            self.lbl_skor.text = f"Puan: {self.puan} | Seviye: {self.seviye}"

    def _ciz(self, ari_x, h):
        self.oyun_alani.canvas.clear()
        with self.oyun_alani.canvas:
            for ex, ey, eh in self.engeller:
                Color(0.47, 0.33, 0.28, 1)
                Rectangle(pos=(ex - 15, ey - eh / 2), size=(30, eh))
                Color(0.22, 0.56, 0.24, 1)
                Ellipse(pos=(ex - 30, ey - eh / 2 - 12), size=(60, 24))

            if self.kalan_mesafe <= 0 and self.bal_kutusu_x is not None:
                Color(1, 0.70, 0.10, 1)
                Ellipse(pos=(self.bal_kutusu_x - 35, h / 2 - 35), size=(70, 70))

            # Ari govdesi
            Color(1, 0.76, 0.03, 1)
            Ellipse(pos=(ari_x - 26, self.ari_y - 18), size=(52, 36))
            Color(0.24, 0.15, 0.14, 1)
            Rectangle(pos=(ari_x - 10, self.ari_y - 16), size=(7, 32))
            Rectangle(pos=(ari_x + 4, self.ari_y - 16), size=(7, 32))
            Color(0.88, 0.95, 0.96, 0.85)
            Ellipse(pos=(ari_x - 12, self.ari_y + 6), size=(18, 20))
            Ellipse(pos=(ari_x + 2, self.ari_y + 6), size=(18, 20))

        self.lbl_skor.text = f"Puan: {self.puan} | Seviye: {self.seviye}"

    def _carpma_sonrasi(self):
        self.app.canlar -= 1
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            if self._olay:
                self._olay.cancel()
            can_bitti_popup_goster(self.app, "ari", None, self.menuye_don)
        else:
            self.ari_dondu = False
            self.ari_y = 300
            self.engeller = []


# ==========================================
# OYUN 3: SEKIL VE RENK AVCISI
# ==========================================
class SekilOyunuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = RenkliArkaplan(renk=(0.44, 0.84, 1, 1))
        self.dis = BoxLayout(orientation="vertical")

        self.lbl_soru = Label(text="", size_hint=(1, None), height=40, bold=True,
                               color=(0, 1, 1, 1))
        self.lbl_durum = Label(text="", size_hint=(1, None), height=28,
                                color=(1, 1, 1, 1))
        self.oyun_alani = Widget()
        self.oyun_alani.bind(on_touch_down=self.dokunuldu)

        self.dis.add_widget(self.lbl_soru)
        self.dis.add_widget(self.lbl_durum)
        self.dis.add_widget(self.oyun_alani)
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
        self.kalan_sure = max(8, 21 - self.seviye)
        self.bulunan = 0

        self.hedef_renk_adi = random.choice(list(RENK_SOZLUGU.keys()))
        self.hedef_renk = RENK_SOZLUGU[self.hedef_renk_adi]
        self.hedef_sekil = random.choice(SEKIL_TIPLERI)
        self.hedef_sayi = random.randint(3, 5)

        self.nesneler = []
        for _ in range(self.hedef_sayi):
            self.nesneler.append({"renk_adi": self.hedef_renk_adi, "renk": self.hedef_renk,
                                   "sekil": self.hedef_sekil, "hedef": True, "bulundu": False})

        celdirici = random.randint(10, 14) + self.seviye
        for _ in range(celdirici):
            r_ad = random.choice(list(RENK_SOZLUGU.keys()))
            s_tip = random.choice(SEKIL_TIPLERI)
            if r_ad == self.hedef_renk_adi and s_tip == self.hedef_sekil:
                s_tip = "Kare" if self.hedef_sekil != "Kare" else "Yuvarlak"
            self.nesneler.append({"renk_adi": r_ad, "renk": RENK_SOZLUGU[r_ad],
                                   "sekil": s_tip, "hedef": False, "bulundu": False})

        random.shuffle(self.nesneler)

        self.lbl_soru.text = f"{self.hedef_sayi} tane {self.hedef_renk_adi} {self.hedef_sekil} bul!"
        self.lbl_durum.text = f"Seviye {self.seviye} | Puan {self.puan} | Sure {self.kalan_sure}"

        Clock.schedule_once(lambda dt: self._konumlandir_ve_ciz(), 0)
        metni_turkce_seslendir(self.lbl_soru.text, bitince_bunu_yap=self._zamanlayici_baslat)

    def _konumlandir_ve_ciz(self):
        w = self.oyun_alani.width or 400
        h = self.oyun_alani.height or 500
        for n in self.nesneler:
            n["x"] = random.uniform(40, max(60, w - 40))
            n["y"] = random.uniform(40, max(60, h - 40))
        self._ciz()

    def _zamanlayici_baslat(self):
        if self._zaman_olay:
            self._zaman_olay.cancel()
        self._zaman_olay = Clock.schedule_interval(self._zaman_adimi, 1)

    def _zaman_adimi(self, dt):
        if not self.oyun_aktif:
            return False
        if self.kalan_sure > 0:
            self.kalan_sure -= 1
            if self.kalan_sure <= 5:
                ses_efekti_cal("tik")
            self.lbl_durum.text = f"Seviye {self.seviye} | Puan {self.puan} | Sure {self.kalan_sure}"
        else:
            self._zaman_olay.cancel()
            self.oyun_aktif = False
            self._can_azalt()
            return False

    def _sekil_ciz(self, n):
        x, y = n["x"], n["y"]
        r = 30
        if n["bulundu"]:
            Color(0.18, 0.80, 0.44, 1)
            Ellipse(pos=(x - r - 8, y - r - 8), size=((r + 8) * 2, (r + 8) * 2))
        Color(*n["renk"])
        s = n["sekil"]
        if s == "Yuvarlak":
            Ellipse(pos=(x - r, y - r), size=(r * 2, r * 2))
        elif s == "Kare":
            Rectangle(pos=(x - r, y - r), size=(r * 2, r * 2))
        elif s == "Ucgen":
            Triangle(points=[x, y + r, x - r, y - r, x + r, y - r])
        elif s == "Yildiz":
            pts = []
            for i in range(10):
                ang = i * math.pi / 5 - math.pi / 2
                rad = r + 4 if i % 2 == 0 else r / 2
                pts.append(x + rad * math.cos(ang))
                pts.append(y + rad * math.sin(ang))
            Line(points=pts + pts[:2], width=1.5, close=True)
            Triangle(points=[x, y + r, x - r * 0.6, y - r * 0.3, x + r * 0.6, y - r * 0.3])

    def _ciz(self):
        self.oyun_alani.canvas.clear()
        with self.oyun_alani.canvas:
            for n in self.nesneler:
                self._sekil_ciz(n)

    def dokunuldu(self, inst, touch):
        if not self.oyun_aktif or not self.oyun_alani.collide_point(*touch.pos):
            return
        for n in self.nesneler:
            if n["bulundu"]:
                continue
            if abs(touch.x - n["x"]) < 35 and abs(touch.y - n["y"]) < 35:
                if n["hedef"]:
                    n["bulundu"] = True
                    self.bulunan += 1
                    self.puan += 10
                    ses_efekti_cal("tin")
                    self.lbl_durum.text = f"Seviye {self.seviye} | Puan {self.puan} | Sure {self.kalan_sure}"
                    self._ciz()
                    if self.bulunan >= self.hedef_sayi:
                        self._kazandi()
                else:
                    self._can_azalt()
                return

    def _kazandi(self):
        self.oyun_aktif = False
        if self._zaman_olay:
            self._zaman_olay.cancel()
        ses_efekti_cal("alkis")
        app = App.get_running_app()
        metni_turkce_seslendir(f"Tebrikler {app.cocuk_ismi}!")
        self.lbl_soru.text = f"TEBRIKLER! Seviye {self.seviye + 1}'e geciliyor..."
        self.seviye += 1
        Clock.schedule_once(lambda dt: self._seviye_yukle(), 2)

    def _can_azalt(self):
        ses_efekti_cal("uzuntu")
        self.app.canlar -= 1
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            if self._zaman_olay:
                self._zaman_olay.cancel()
            can_bitti_popup_goster(self.app, "sekil", None, self.menuye_don)
        else:
            self._ciz()


# ==========================================
# OYUN 4: SURPRIZ BULMACA KULESI (KART ESLESTIRME)
# ==========================================
class BulmacaOyunuEkrani(Screen):
    SEMBOLLER = ["Kopek", "Kedi", "Elma", "Muz", "Araba", "Roket",
                 "Balon", "Yildiz", "Panda", "Kurbaga", "Uzum", "Cilek"]
    SEMBOL_RENK = {
        "Kopek": (0.55, 0.35, 0.20, 1), "Kedi": (0.9, 0.6, 0.2, 1),
        "Elma": (0.85, 0.15, 0.15, 1), "Muz": (0.95, 0.85, 0.1, 1),
        "Araba": (0.15, 0.5, 0.85, 1), "Roket": (0.6, 0.6, 0.65, 1),
        "Balon": (0.9, 0.2, 0.5, 1), "Yildiz": (0.95, 0.75, 0.1, 1),
        "Panda": (0.2, 0.2, 0.2, 1), "Kurbaga": (0.2, 0.75, 0.3, 1),
        "Uzum": (0.45, 0.15, 0.6, 1), "Cilek": (0.85, 0.1, 0.35, 1),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = RenkliArkaplan(renk=(0.44, 0.84, 1, 1))
        self.dis = BoxLayout(orientation="vertical")

        self.lbl_durum = Label(text="", size_hint=(1, None), height=36, bold=True,
                                color=(0, 1, 1, 1))
        self.oyun_alani = Widget()
        self.oyun_alani.bind(on_touch_down=self.dokunuldu)

        self.dis.add_widget(self.lbl_durum)
        self.dis.add_widget(self.oyun_alani)
        self.kok.add_widget(self.dis)
        self.add_widget(self.kok)
        self.ust_panel = None
        self._ezber_olay = None
        self.kartlar = []
        self.kule_blok = 0

    def _panel_kur(self):
        if self.ust_panel is None:
            self.ust_panel = UstPanel(self.app, self.menuye_don)
            self.dis.add_widget(self.ust_panel, index=len(self.dis.children))

    def menuye_don(self):
        self.oyun_aktif = False
        if self._ezber_olay:
            self._ezber_olay.cancel()
        self.manager.current = "menu"

    def oyunu_baslat(self):
        self.app = App.get_running_app()
        self._panel_kur()
        self.seviye = 1
        self.puan = 0
        self.kule_blok = 0
        muzik_ses_seviyesi_ayarla(0.2)
        self._seviye_yukle()

    def _seviye_yukle(self):
        self.oyun_aktif = True
        self.secilenler = []
        self.eslesen_cift = 0
        self.tiklama_kilitli = True
        self.ezber_suresi = 5

        if self.seviye == 1:
            self.toplam_cift, self.grid_cols = 3, 3
        elif self.seviye == 2:
            self.toplam_cift, self.grid_cols = 4, 4
        else:
            self.toplam_cift, self.grid_cols = 6, 4

        secilen = random.sample(self.SEMBOLLER, self.toplam_cift)
        liste = secilen * 2
        random.shuffle(liste)
        self.kartlar = [{"sembol": s, "acik": True, "eslesdi": False} for s in liste]

        self.lbl_durum.text = f"Seviye {self.seviye} | Puan {self.puan}"
        Clock.schedule_once(lambda dt: self._ciz(), 0)
        metni_turkce_seslendir("Kartlari aklinda tut!")
        if self._ezber_olay:
            self._ezber_olay.cancel()
        self._ezber_olay = Clock.schedule_interval(self._ezber_adimi, 1)

    def _ezber_adimi(self, dt):
        if not self.oyun_aktif:
            return False
        if self.ezber_suresi > 0:
            ses_efekti_cal("tik")
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
        w = self.oyun_alani.width or 400
        h = self.oyun_alani.height or 500
        cols = self.grid_cols
        rows = math.ceil(len(self.kartlar) / cols)
        card_w = min(100, (w - 20) / cols - 12)
        card_h = card_w * 1.2
        toplam_w = cols * (card_w + 12) - 12
        toplam_h = rows * (card_h + 12) - 12
        start_x = (w - toplam_w) / 2
        start_y = h - 20 - toplam_h
        col = idx % cols
        row = idx // cols
        x = start_x + col * (card_w + 12)
        y = start_y + (rows - 1 - row) * (card_h + 12)
        return x, y, card_w, card_h

    def _ciz(self):
        self.oyun_alani.canvas.clear()
        with self.oyun_alani.canvas:
            # kule
            w = self.oyun_alani.width or 400
            blok_h = 18
            kule_renkleri = [(0.9, 0.3, 0.3, 1), (0.95, 0.8, 0.1, 1), (0.2, 0.8, 0.4, 1),
                              (0.2, 0.6, 0.9, 1), (0.6, 0.35, 0.7, 1)]
            for i in range(self.kule_blok):
                Color(*kule_renkleri[i % len(kule_renkleri)])
                Rectangle(pos=(w - 70, 10 + i * blok_h), size=(50, blok_h - 3))

            for idx, kart in enumerate(self.kartlar):
                x, y, cw, ch = self._kart_konumu(idx)
                if kart["eslesdi"]:
                    Color(0.78, 0.90, 0.79, 1)
                    Rectangle(pos=(x, y), size=(cw, ch))
                    Color(*self.SEMBOL_RENK.get(kart["sembol"], (1, 1, 1, 1)))
                    Ellipse(pos=(x + cw * 0.25, y + ch * 0.25), size=(cw * 0.5, ch * 0.5))
                elif kart["acik"]:
                    Color(1, 1, 0.9, 1)
                    Rectangle(pos=(x, y), size=(cw, ch))
                    Color(*self.SEMBOL_RENK.get(kart["sembol"], (1, 1, 1, 1)))
                    Ellipse(pos=(x + cw * 0.25, y + ch * 0.25), size=(cw * 0.5, ch * 0.5))
                else:
                    Color(0.20, 0.60, 0.86, 1)
                    Rectangle(pos=(x, y), size=(cw, ch))
                    Color(1, 1, 1, 1)
                    Line(rectangle=(x, y, cw, ch), width=1.5)

        durum = f"Kartlari Incele: {self.ezber_suresi + 1} sn" if (self.ezber_suresi > 0 and self.tiklama_kilitli) else "Eslesenleri Bul!"
        self.lbl_durum.text = f"Seviye {self.seviye} | Puan {self.puan} | {durum}"

    def dokunuldu(self, inst, touch):
        if not self.oyun_aktif or self.tiklama_kilitli or not self.oyun_alani.collide_point(*touch.pos):
            return
        for idx, kart in enumerate(self.kartlar):
            if kart["acik"] or kart["eslesdi"]:
                continue
            x, y, cw, ch = self._kart_konumu(idx)
            if x <= touch.x <= x + cw and y <= touch.y <= y + ch:
                ses_efekti_cal("tik")
                kart["acik"] = True
                self.secilenler.append(kart)
                self._ciz()
                if len(self.secilenler) == 2:
                    self.tiklama_kilitli = True
                    k1, k2 = self.secilenler
                    if k1["sembol"] == k2["sembol"]:
                        ses_efekti_cal("tin")
                        k1["eslesdi"] = True
                        k2["eslesdi"] = True
                        self.eslesen_cift += 1
                        self.puan += 15
                        self.kule_blok += 1
                        self.secilenler = []
                        self.tiklama_kilitli = False
                        self._ciz()
                        if self.eslesen_cift >= self.toplam_cift:
                            self._kazandi()
                    else:
                        Clock.schedule_once(lambda dt: self._kapat(k1, k2), 0.7)
                return

    def _kapat(self, k1, k2):
        k1["acik"] = False
        k2["acik"] = False
        self.secilenler = []
        self.tiklama_kilitli = False
        self._can_azalt()

    def _kazandi(self):
        self.oyun_aktif = False
        ses_efekti_cal("alkis")
        app = App.get_running_app()
        metni_turkce_seslendir(f"Tebrikler {app.cocuk_ismi}!")
        self.lbl_durum.text = f"KULE BUYUYOR! Seviye {self.seviye + 1}'e geciliyor..."
        self.seviye += 1
        Clock.schedule_once(lambda dt: self._seviye_yukle(), 2)

    def _can_azalt(self):
        self.app.canlar -= 1
        ses_efekti_cal("uzuntu")
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            can_bitti_popup_goster(self.app, "bulmaca", None, self.menuye_don)
        else:
            self._ciz()


# ==========================================
# ANA UYGULAMA
# ==========================================
class MinikKasiflerApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        self.cocuk_ismi = "Minik Kasif"
        self.canlar = 3
        self.max_can = 3
        self.can_yenilenme_suresi = 180
        self.kalan_can_suresi = self.can_yenilenme_suresi

        # gecici ses dosyalarini temizle
        kok = os.path.dirname(os.path.abspath(__file__))
        for f in os.listdir(kok):
            if f.startswith("gecici_ses_"):
                try:
                    os.remove(os.path.join(kok, f))
                except Exception:
                    pass

        muzik_baslat()
        Clock.schedule_interval(self._can_zamanlayicisi, 1)

        sm = ScreenManager()
        sm.add_widget(GirisEkrani(name="giris"))
        sm.add_widget(MenuEkrani(name="menu"))
        sm.add_widget(BalonOyunuEkrani(name="balon"))
        sm.add_widget(AriOyunuEkrani(name="ari"))
        sm.add_widget(SekilOyunuEkrani(name="sekil"))
        sm.add_widget(BulmacaOyunuEkrani(name="bulmaca"))
        sm.current = "giris"
        return sm

    def _can_zamanlayicisi(self, dt):
        if self.canlar < self.max_can:
            self.kalan_can_suresi -= 1
            if self.kalan_can_suresi <= 0:
                self.canlar += 1
                self.kalan_can_suresi = self.can_yenilenme_suresi
        else:
            self.kalan_can_suresi = self.can_yenilenme_suresi


if __name__ == "__main__":
    MinikKasiflerApp().run()
